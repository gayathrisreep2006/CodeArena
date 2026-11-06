from django.conf import settings
from django.db import models


class Submission(models.Model):
    PENDING, ACCEPTED, WRONG, TLE, ERROR = "pending", "accepted", "wrong_answer", "time_limit", "error"
    VERDICT_CHOICES = [
        (PENDING, "Pending"),
        (ACCEPTED, "Accepted"),
        (WRONG, "Wrong Answer"),
        (TLE, "Time Limit Exceeded"),
        (ERROR, "Runtime Error"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="submissions")
    problem = models.ForeignKey("problems.Problem", on_delete=models.CASCADE, related_name="submissions")
    room = models.ForeignKey("arena.Room", on_delete=models.SET_NULL, null=True, blank=True, related_name="submissions")
    code = models.TextField()
    verdict = models.CharField(max_length=15, choices=VERDICT_CHOICES, default=PENDING)
    passed_cases = models.PositiveIntegerField(default=0)
    total_cases = models.PositiveIntegerField(default=0)
    runtime_ms = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"{self.user.username} -> {self.problem.title}: {self.verdict}"
