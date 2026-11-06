import csv

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from accounts.permissions import host_required
from arena.models import Room
from arena.services import build_leaderboard
from judge.models import Submission
from problems.models import Problem


def home(request):
    context = {
        "problem_count": Problem.objects.filter(is_published=True).count(),
        "room_count": Room.objects.count(),
        "submission_count": Submission.objects.count(),
    }
    return render(request, "home.html", context)


@login_required
def dashboard(request):
    accepted = Q(verdict=Submission.ACCEPTED)

    # personal stats (every role)
    mine = Submission.objects.filter(user=request.user)
    my_total = mine.count()
    my_accepted = mine.filter(accepted).count()
    my_stats = {
        "total": my_total,
        "accepted": my_accepted,
        "solved": mine.filter(accepted).values("problem").distinct().count(),
        "rate": round(my_accepted * 100 / my_total) if my_total else 0,
    }

    # platform stats
    total_subs = Submission.objects.count()
    verdicts = []
    for value, label in Submission.VERDICT_CHOICES:
        count = Submission.objects.filter(verdict=value).count()
        verdicts.append({"label": label, "count": count,
                         "percent": round(count * 100 / total_subs) if total_subs else 0})

    top_solvers = (User.objects
                   .annotate(solved=Count("submissions__problem", filter=Q(submissions__verdict="accepted"), distinct=True))
                   .filter(solved__gt=0).order_by("-solved", "username")[:5])

    busiest_problems = (Problem.objects
                        .annotate(total=Count("submissions"),
                                  ok=Count("submissions", filter=Q(submissions__verdict="accepted")))
                        .filter(total__gt=0).order_by("-total")[:5])
    for p in busiest_problems:
        p.rate = round(p.ok * 100 / p.total)

    context = {
        "my": my_stats,
        "cards": {
            "users": User.objects.count(),
            "problems": Problem.objects.filter(is_published=True).count(),
            "rooms": Room.objects.count(),
            "live_rooms": Room.objects.filter(status=Room.LIVE).count(),
            "submissions": total_subs,
        },
        "verdicts": verdicts,
        "top_solvers": top_solvers,
        "busiest_problems": busiest_problems,
    }
    return render(request, "dashboard/dashboard.html", context)


def _safe(value):
    """Stop spreadsheet formula injection: cells starting with = + - @ get a leading quote."""
    text = str(value)
    return "'" + text if text[:1] in ("=", "+", "-", "@") else text


@host_required
def export_submissions_csv(request):
    """Host: submissions to own problems or own rooms. Admin: everything."""
    subs = Submission.objects.select_related("user", "problem", "room").order_by("-submitted_at")
    if request.user.profile.role != "admin":
        subs = subs.filter(Q(problem__created_by=request.user) | Q(room__host=request.user))

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="submissions.csv"'
    writer = csv.writer(response)
    writer.writerow(["id", "user", "problem", "contest", "verdict", "passed", "total", "runtime_ms", "submitted_at"])
    for s in subs:
        writer.writerow([s.pk, _safe(s.user.username), _safe(s.problem.title), s.room.code if s.room else "",
                         s.verdict, s.passed_cases, s.total_cases, s.runtime_ms,
                         s.submitted_at.strftime("%Y-%m-%d %H:%M:%S")])
    return response


@login_required
def export_room_results_csv(request, code):
    room = get_object_or_404(Room, code=code)
    if room.host_id != request.user.id and request.user.profile.role != "admin":
        raise PermissionDenied
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="results_{room.code}.csv"'
    writer = csv.writer(response)
    writer.writerow(["rank", "player", "problems_solved", "score", "penalty_minutes", "wrong_attempts"])
    for row in build_leaderboard(room):
        writer.writerow([row["rank"], _safe(row["username"]), row["solved"], row["score"], row["penalty"], row["wrong"]])
    return response
