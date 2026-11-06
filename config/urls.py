from django.contrib import admin
from django.urls import include, path

from dashboard.views import home

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("accounts/", include("accounts.urls")),
    path("problems/", include("problems.urls")),
    path("judge/", include("judge.urls")),
    path("arena/", include("arena.urls")),
    path("dashboard/", include("dashboard.urls")),
]
