from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.permissions import host_required

from .forms import JoinForm, RoomForm
from .models import Participant, Room
from .services import build_leaderboard


def _can_manage(user, room):
    return room.host_id == user.id or user.profile.role == "admin"


@login_required
def room_list(request):
    for live_room in Room.objects.filter(status=Room.LIVE):
        live_room.sync_status()  # close rooms whose time is over before listing
    rooms = Room.objects.select_related("host").annotate(player_count=Count("participants"))
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")
    if q:
        rooms = rooms.filter(Q(title__icontains=q) | Q(code__icontains=q))
    if status in ("waiting", "live", "finished"):
        rooms = rooms.filter(status=status)
    page_obj = Paginator(rooms, 8).get_page(request.GET.get("page"))
    extra = ""
    if q:
        extra += f"&q={q}"
    if status:
        extra += f"&status={status}"
    return render(request, "arena/room_list.html", {
        "page_obj": page_obj, "q": q, "status": status, "extra_query": extra,
        "join_form": JoinForm(),
    })


@host_required
def room_create(request):
    form = RoomForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        room = form.save(commit=False)
        room.host = request.user
        room.save()
        form.save_m2m()
        messages.success(request, f"Room created. Share the code {room.code} with players.")
        return redirect("arena:detail", code=room.code)
    return render(request, "arena/room_form.html", {"form": form})


@login_required
def room_join(request):
    if request.method != "POST":
        return redirect("arena:list")
    form = JoinForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Enter a valid 6-character room code.")
        return redirect("arena:list")
    room = Room.objects.filter(code=form.cleaned_data["code"]).first()
    if room is None:
        messages.error(request, "No room found with that code.")
        return redirect("arena:list")
    room.sync_status()
    if room.status == Room.FINISHED:
        messages.error(request, "This contest has already finished.")
        return redirect("arena:detail", code=room.code)
    Participant.objects.get_or_create(room=room, user=request.user)
    messages.success(request, f"You joined {room.title}.")
    return redirect("arena:detail", code=room.code)


@login_required
def room_detail(request, code):
    room = get_object_or_404(Room.objects.select_related("host"), code=code)
    room.sync_status()
    is_participant = room.participants.filter(user=request.user).exists()
    return render(request, "arena/room_detail.html", {
        "room": room,
        "problems": room.problems.all(),
        "leaderboard": build_leaderboard(room),
        "is_participant": is_participant,
        "can_manage": _can_manage(request.user, room),
        "remaining": room.remaining_seconds(),
    })


@login_required
def room_start(request, code):
    room = get_object_or_404(Room, code=code)
    if not _can_manage(request.user, room):
        raise PermissionDenied
    if request.method == "POST":
        if room.status != Room.WAITING:
            messages.error(request, "Only a waiting room can be started.")
        elif not room.problems.exists():
            messages.error(request, "Add at least one problem first.")
        else:
            room.status = Room.LIVE
            room.start_time = timezone.now()
            room.save(update_fields=["status", "start_time"])
            messages.success(request, "Contest started. Good luck!")
    return redirect("arena:detail", code=room.code)


@login_required
def room_finish(request, code):
    room = get_object_or_404(Room, code=code)
    if not _can_manage(request.user, room):
        raise PermissionDenied
    if request.method == "POST" and room.status == Room.LIVE:
        room.status = Room.FINISHED
        room.save(update_fields=["status"])
        messages.success(request, "Contest finished.")
    return redirect("arena:detail", code=room.code)


@login_required
def leaderboard_json(request, code):
    """JSON endpoint polled by JavaScript every few seconds."""
    room = get_object_or_404(Room, code=code)
    room.sync_status()
    return JsonResponse({
        "code": room.code,
        "status": room.status,
        "remaining_seconds": room.remaining_seconds(),
        "leaderboard": build_leaderboard(room),
    })
