from collections import defaultdict

from django.contrib import admin, messages

from . import service
from .models import Device


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "name",
        "user",
        "active",
        "type",
        "token",
        "created_at",
        "updated_at",
    ]
    list_filter = ["active", "type"]
    actions = ["send_notification"]
    search_fields = ["name", "token", "user__id", "user__email"]

    autocomplete_fields = ("user",)

    def send_notification(self, request, queryset):
        """
        Send a test notification immediately.

        Will parse and represent any errors encountered, expecting a response
        structure similar to the following:

            {
                "multicast_ids": [123456789],
                "success": 0,
                "failure": 1,
                "canonical_ids": 0,
                "results": [
                    {"error": "InvalidRegistration"}
                ],
                "topic_message_id": None
            }
        """
        success = errors = 0
        error_counts = defaultdict(int)
        for device in queryset.iterator():
            response = service.get_fcm_backend().send_notification(
                device, title="Testing 123", body="A test notification"
            )
            if int(response["success"]):
                success += 1
            elif int(response["failure"]):
                errors += 1
                for e in response["results"]:
                    error_counts[e.get("error")] += 1
        if success:
            self.message_user(
                request, f"{success} notifications were sent successfully."
            )
        if errors:
            self.message_user(
                request,
                f"{errors} notifications hit errors: {dict(error_counts)}",
                level=messages.WARNING,
            )

    send_notification.short_description = "Send test notification (immediate)"
