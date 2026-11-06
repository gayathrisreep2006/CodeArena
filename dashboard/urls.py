from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard, name="index"),
    path("export/submissions/", views.export_submissions_csv, name="submissions_csv"),
    path("export/room/<str:code>/", views.export_room_results_csv, name="room_csv"),
]
