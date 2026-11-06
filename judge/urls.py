from django.urls import path

from . import views

app_name = "judge"

urlpatterns = [
    path("submit/<int:problem_id>/", views.submit, name="submit"),
    path("submission/<int:pk>/", views.submission_detail, name="detail"),
    path("my-submissions/", views.my_submissions, name="my_submissions"),
]
