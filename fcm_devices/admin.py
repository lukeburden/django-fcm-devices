from collections import defaultdict

from django.contrib import admin, messages
from django.core.exceptions import ImproperlyConfigured

from pyfcm.errors import FCMError

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

        With the FCM v1 API a successful send returns the message identifier,
        e.g. {"name": "projects/myproject/messages/0:1500415314455276%31bd1c96"}.
        Failures are raised as PyFCM errors, except for unregistered tokens which
        the backend handles by deactivating the device and returning None.
        """
        success = errors = 0
        error_counts = defaultdict(int)
        backend = service.get_fcm_backend()
        for device in queryset.iterator():
            try:
                response = backend.send_notification(
                    device,
                    notification_title="Testing 123",
                    notification_body="A test notification",
                )
            except (FCMError, ImproperlyConfigured) as e:
                errors += 1
                error_counts[e.__class__.__name__] += 1
                continue
            if response and response.get("name"):
                success += 1
            else:
                errors += 1
                error_counts["FCMNotRegisteredError"] += 1
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
