from django.contrib import admin

from .models import Submission


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("user", "problem", "room", "verdict", "passed_cases", "total_cases", "submitted_at")
    list_filter = ("verdict",)
