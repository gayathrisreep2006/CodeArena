from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from arena.models import Room
from problems.models import Problem

from .models import Submission
from .runner import judge_submission

MAX_CODE_LENGTH = 20000


@login_required
@require_POST
def submit(request, problem_id):
    problem = get_object_or_404(Problem, pk=problem_id)
    if not problem.is_published and problem.created_by_id != request.user.id:
        raise PermissionDenied

    code = request.POST.get("code", "").strip()
    room_code = request.POST.get("room", "").strip().upper()
    back = redirect("problems:detail", pk=problem.pk)

    if not code:
        messages.error(request, "Please write some code before submitting.")
        return back
    if len(code) > MAX_CODE_LENGTH:
        messages.error(request, f"Code is too long (limit {MAX_CODE_LENGTH} characters).")
        return back

    room = None
    if room_code:
        room = get_object_or_404(Room, code=room_code)
        back = redirect(f"{problem.get_absolute_url()}?room={room.code}")
        if not room.is_open():
            messages.error(request, "This contest is not live, so submissions are closed.")
            return back
        if not room.participants.filter(user=request.user).exists():
            messages.error(request, "Join the contest before submitting.")
            return back
        if not room.problems.filter(pk=problem.pk).exists():
            messages.error(request, "This problem is not part of the contest.")
            return back

    submission = Submission.objects.create(user=request.user, problem=problem, room=room, code=code)
    judge_submission(submission)
    messages.info(request, f"Verdict: {submission.get_verdict_display()}")
    return redirect("judge:detail", pk=submission.pk)


@login_required
def submission_detail(request, pk):
    submission = get_object_or_404(Submission.objects.select_related("problem", "room", "user"), pk=pk)
    user = request.user
    allowed = (
        submission.user_id == user.id
        or user.profile.role == "admin"
        or (submission.room_id and submission.room.host_id == user.id)
    )
    if not allowed:
        raise PermissionDenied
    return render(request, "judge/submission_detail.html", {"s": submission})


@login_required
def my_submissions(request):
    submissions = Submission.objects.filter(user=request.user).select_related("problem", "room")
    verdict = request.GET.get("verdict", "")
    if verdict in dict(Submission.VERDICT_CHOICES):
        submissions = submissions.filter(verdict=verdict)
    page_obj = Paginator(submissions, 10).get_page(request.GET.get("page"))
    extra = f"&verdict={verdict}" if verdict else ""
    return render(request, "judge/my_submissions.html", {
        "page_obj": page_obj, "verdict": verdict, "extra_query": extra,
        "verdict_choices": Submission.VERDICT_CHOICES,
    })
