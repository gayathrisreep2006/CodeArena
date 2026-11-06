from django.conf import settings
from django.db import models


class Profile(models.Model):
    """Extra data for every user. `role` drives all access control."""

    PLAYER = "player"
    HOST = "host"
    ADMIN = "admin"
    ROLE_CHOICES = [(PLAYER, "Player"), (HOST, "Host"), (ADMIN, "Admin")]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=PLAYER)
    bio = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

    @property
    def is_host(self):
        return self.role in (self.HOST, self.ADMIN)

    @property
    def is_admin_role(self):
        return self.role == self.ADMIN
