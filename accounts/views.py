from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProfileForm, RegisterForm, RoleForm
from .permissions import admin_required


def register(request):
    if request.user.is_authenticated:
        return redirect("home")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Welcome to CodeArena!")
        return redirect("home")
    return render(request, "accounts/register.html", {"form": form})


@login_required
def profile(request):
    form = ProfileForm(request.POST or None, instance=request.user.profile)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profile updated.")
        return redirect("accounts:profile")
    return render(request, "accounts/profile.html", {"form": form})


@admin_required
def user_list(request):
    """Admin only: search users by name/email, filter by role, paginate."""
    users = User.objects.select_related("profile").order_by("username")
    q = request.GET.get("q", "").strip()
    role = request.GET.get("role", "")
    if q:
        users = users.filter(Q(username__icontains=q) | Q(email__icontains=q))
    if role in ("player", "host", "admin"):
        users = users.filter(profile__role=role)
    page_obj = Paginator(users, 10).get_page(request.GET.get("page"))
    extra = ""
    if q:
        extra += f"&q={q}"
    if role:
        extra += f"&role={role}"
    return render(request, "accounts/user_list.html",
                  {"page_obj": page_obj, "q": q, "role": role, "extra_query": extra})


@admin_required
def change_role(request, user_id):
    """Admin only (POST): change the role of another user."""
    target = get_object_or_404(User, pk=user_id)
    if request.method == "POST":
        if target == request.user:
            messages.error(request, "You cannot change your own role.")
        else:
            form = RoleForm(request.POST, instance=target.profile)
            if form.is_valid():
                form.save()
                messages.success(request, f"{target.username} is now {target.profile.role}.")
            else:
                messages.error(request, "Invalid role.")
    return redirect("accounts:user_list")
