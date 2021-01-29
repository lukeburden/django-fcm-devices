from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

from pyfcm import FCMNotification

from .settings import app_settings
from .signals import device_updated


# categorise common errors in terms of what we"ll do
unrecoverable_errors = set(
    ["MissingRegistration", "InvalidRegistration", "NotRegistered"]
)
configuration_errors = set(["MismatchSenderId"])


class FCMBackend(object):
    """You can override this class to customise sending of notifications."""

    def send_notification(self, device, **kwargs):
        push_service = FCMNotification(api_key=app_settings.API_KEY)
        result = push_service.notify_single_device(
            registration_id=device.token,
            **kwargs,
        )
        self.update_device_on_error(device, result)
        return result

    def update_device_on_error(self, device, result):
        """
        If a device fails to be sent a notification due to an unrecoverable
        issue we want to ensure we don't try again.

        See `unrecoverable_errors` for which we act upon.
        """
        if result["failure"] > 0:
            if result["results"][0]["error"] in unrecoverable_errors:
                device.active = False
                device.save(update_fields=("active", "updated_at"))
                device_updated.send(sender=device.__class__, device=device)
            elif result["results"][0]["error"] in configuration_errors:
                raise ImproperlyConfigured(
                    f"FCM configuration problem sending to device {device.id}: "
                    f"{result['results'][0]['error']}"
                )


class ConsoleFCMBackend(FCMBackend):
    """Console FCM backend for development environments."""

    def send_notification(self, device, **kwargs):
        print(f"Push to {device}\nPyFCM kwargs: {kwargs}\n")
        # this is a partial response, but the part our sending code will be looking for
        return {"success": 1, "failure": 0}


def get_fcm_backend():
    cls = app_settings.BACKEND_CLASS
    if cls is None:
        # default to console to avoid accidental push notifications
        return ConsoleFCMBackend()
    return import_string(cls)()
