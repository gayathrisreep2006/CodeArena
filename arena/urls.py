from django.urls import path

from . import views

app_name = "arena"

urlpatterns = [
    path("", views.room_list, name="list"),
    path("new/", views.room_create, name="create"),
    path("join/", views.room_join, name="join"),
    path("<str:code>/", views.room_detail, name="detail"),
    path("<str:code>/start/", views.room_start, name="start"),
    path("<str:code>/finish/", views.room_finish, name="finish"),
    path("<str:code>/leaderboard.json", views.leaderboard_json, name="leaderboard_json"),
]
