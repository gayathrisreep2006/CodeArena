import random
import string
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


def generate_room_code():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))


class Room(models.Model):
    WAITING, LIVE, FINISHED = "waiting", "live", "finished"
    STATUS_CHOICES = [(WAITING, "Waiting"), (LIVE, "Live"), (FINISHED, "Finished")]

    code = models.CharField(max_length=6, unique=True, default=generate_room_code)
    title = models.CharField(max_length=120)
    host = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="hosted_rooms")
    problems = models.ManyToManyField("problems.Problem", related_name="rooms")
    duration_minutes = models.PositiveIntegerField(default=30)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=WAITING)
    start_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} [{self.code}]"

    @property
    def end_time(self):
        if not self.start_time:
            return None
        return self.start_time + timedelta(minutes=self.duration_minutes)

    def sync_status(self):
        """A live room whose time is over becomes Finished automatically."""
        if self.status == self.LIVE and self.end_time and timezone.now() >= self.end_time:
            self.status = self.FINISHED
            self.save(update_fields=["status"])
        return self

    def is_open(self):
        """True only while the contest is live and time remains."""
        return self.sync_status().status == self.LIVE

    def remaining_seconds(self):
        if self.status != self.LIVE or not self.end_time:
            return 0
        return max(0, int((self.end_time - timezone.now()).total_seconds()))


class Participant(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="participants")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="participations")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["room", "user"], name="unique_participant_per_room")]

    def __str__(self):
        return f"{self.user.username} in {self.room.code}"
