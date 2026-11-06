from django.urls import path

from . import views

app_name = "problems"

urlpatterns = [
    path("", views.problem_list, name="list"),
    path("new/", views.problem_create, name="create"),
    path("<int:pk>/", views.problem_detail, name="detail"),
    path("<int:pk>/edit/", views.problem_edit, name="edit"),
    path("<int:pk>/delete/", views.problem_delete, name="delete"),
    path("<int:pk>/testcases/", views.testcase_manage, name="testcases"),
    path("<int:pk>/testcases/<int:case_id>/delete/", views.testcase_delete, name="testcase_delete"),
]
