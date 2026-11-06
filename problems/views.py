from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from accounts.permissions import host_required
from judge.models import Submission

from .forms import ProblemForm, TestCaseForm
from .models import Problem, TestCase


def _can_manage(user, problem):
    """Owner of the problem or an Admin may edit/delete it."""
    return user.is_authenticated and (problem.created_by_id == user.id or user.profile.role == "admin")


def problem_list(request):
    problems = Problem.objects.select_related("created_by")
    if request.user.is_authenticated:
        problems = problems.filter(Q(is_published=True) | Q(created_by=request.user))
    else:
        problems = problems.filter(is_published=True)

    q = request.GET.get("q", "").strip()
    difficulty = request.GET.get("difficulty", "")
    if q:
        problems = problems.filter(Q(title__icontains=q) | Q(description__icontains=q))
    if difficulty in ("easy", "medium", "hard"):
        problems = problems.filter(difficulty=difficulty)

    page_obj = Paginator(problems, 8).get_page(request.GET.get("page"))
    solved_ids = set()
    if request.user.is_authenticated:
        solved_ids = set(Submission.objects.filter(user=request.user, verdict=Submission.ACCEPTED)
                         .values_list("problem_id", flat=True))
    extra = ""
    if q:
        extra += f"&q={q}"
    if difficulty:
        extra += f"&difficulty={difficulty}"
    return render(request, "problems/problem_list.html", {
        "page_obj": page_obj, "q": q, "difficulty": difficulty,
        "solved_ids": solved_ids, "extra_query": extra,
    })


def problem_detail(request, pk):
    problem = get_object_or_404(Problem, pk=pk)
    if not problem.is_published and not _can_manage(request.user, problem):
        raise Http404
    context = {
        "problem": problem,
        "samples": problem.test_cases.filter(is_sample=True),  # hidden cases are never shown
        "can_manage": _can_manage(request.user, problem),
        "room_code": request.GET.get("room", ""),
    }
    if request.user.is_authenticated:
        context["my_submissions"] = problem.submissions.filter(user=request.user)[:5]
    return render(request, "problems/problem_detail.html", context)


@host_required
def problem_create(request):
    form = ProblemForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        problem = form.save(commit=False)
        problem.created_by = request.user
        problem.save()
        messages.success(request, "Problem created. Now add test cases.")
        return redirect("problems:testcases", pk=problem.pk)
    return render(request, "problems/problem_form.html", {"form": form, "heading": "Create problem"})


@login_required
def problem_edit(request, pk):
    problem = get_object_or_404(Problem, pk=pk)
    if not _can_manage(request.user, problem):
        raise PermissionDenied
    form = ProblemForm(request.POST or None, instance=problem)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Problem updated.")
        return redirect("problems:detail", pk=problem.pk)
    return render(request, "problems/problem_form.html", {"form": form, "heading": "Edit problem"})


@login_required
def problem_delete(request, pk):
    problem = get_object_or_404(Problem, pk=pk)
    if not _can_manage(request.user, problem):
        raise PermissionDenied
    if request.method == "POST":
        problem.delete()
        messages.success(request, "Problem deleted.")
        return redirect("problems:list")
    return render(request, "problems/problem_confirm_delete.html", {"problem": problem})


@login_required
def testcase_manage(request, pk):
    """List the test cases of a problem and add a new one."""
    problem = get_object_or_404(Problem, pk=pk)
    if not _can_manage(request.user, problem):
        raise PermissionDenied
    form = TestCaseForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        case = form.save(commit=False)
        case.problem = problem
        case.save()
        messages.success(request, "Test case added.")
        return redirect("problems:testcases", pk=problem.pk)
    return render(request, "problems/testcases.html", {
        "problem": problem, "form": form, "cases": problem.test_cases.all(),
    })


@login_required
def testcase_delete(request, pk, case_id):
    problem = get_object_or_404(Problem, pk=pk)
    if not _can_manage(request.user, problem):
        raise PermissionDenied
    if request.method == "POST":
        get_object_or_404(TestCase, pk=case_id, problem=problem).delete()
        messages.success(request, "Test case deleted.")
    return redirect("problems:testcases", pk=problem.pk)
