from django.conf import settings
from django.db import models
from django.urls import reverse


class Problem(models.Model):
    EASY, MEDIUM, HARD = "easy", "medium", "hard"
    DIFFICULTY_CHOICES = [(EASY, "Easy"), (MEDIUM, "Medium"), (HARD, "Hard")]

    title = models.CharField(max_length=150, unique=True)
    description = models.TextField(help_text="Explain the problem, input format and output format.")
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default=EASY)
    points = models.PositiveIntegerField(default=100)
    time_limit = models.PositiveIntegerField(default=2, help_text="Seconds allowed per test case")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="problems")
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("problems:detail", args=[self.pk])


class TestCase(models.Model):
    __test__ = False  # stop pytest/unittest from treating this model as a test class

    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="test_cases")
    input_data = models.TextField(blank=True, help_text="Text given to the program on stdin")
    expected_output = models.TextField()
    is_sample = models.BooleanField(default=False, help_text="Sample cases are shown to players; others stay hidden")

    def __str__(self):
        return f"Test case #{self.pk} of {self.problem.title}"
