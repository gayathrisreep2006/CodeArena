from django.contrib import admin

from .models import Participant, Room

admin.site.register(Participant)


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("title", "code", "host", "status", "created_at")
    list_filter = ("status",)
