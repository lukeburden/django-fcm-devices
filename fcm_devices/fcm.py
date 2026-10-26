from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

from google.oauth2 import service_account
from pyfcm import FCMNotification
from pyfcm.errors import FCMNotRegisteredError, FCMSenderIdMismatchError

from .settings import app_settings
from .signals import device_updated


class FCMBackend(object):
    """You can override this class to customise sending of notifications."""

    def send_notification(self, device, **kwargs):
        credentials = service_account.Credentials.from_service_account_info(
            app_settings.GOOGLE_SERVICE_ACCOUNT_INFO,
            scopes=["https://www.googleapis.com/auth/firebase.messaging"],
        )
        project_id = getattr(credentials, "project_id", None)
        if not project_id:
            raise ImproperlyConfigured(
                "GOOGLE_SERVICE_ACCOUNT_INFO must specify a project_id."
            )
        # PyFCM supports loading from service file directly, OR passing in credentials.
        push_service = FCMNotification(credentials=credentials)
        # NOTE: In the firebase messaging V1 API (and thus PyFCM 2.x), the API response is simply a dictionary with one field, 'name',
        # which is the identifier of the message sent, in the format of projects/*/messages/{message_id}.
        # Errors are raised and there is no longer a 'failure' key in the response to parse.
        result = None
        try:
            result = push_service.notify(
                fcm_token=device.token,
                **kwargs,
            )

        # missing, unregistered, and invalid. see
        # https://firebase.google.com/docs/reference/fcm/rest/v1/ErrorCode
        except FCMNotRegisteredError:
            self.update_device_on_registration_error(device)

        except FCMSenderIdMismatchError:
            self.update_device_on_registration_error(device)
            raise ImproperlyConfigured(
                "The authenticated sender ID is different from the sender ID"
                " of the registration token."
            )

        return result

    def update_device_on_registration_error(self, device):
        """
        If a device fails to be sent a notification due to an unrecoverable
        issue we want to ensure we don't try again.
        """
        device.active = False
        device.save(update_fields=("active", "updated_at"))
        device_updated.send(sender=device.__class__, device=device)


class ConsoleFCMBackend(FCMBackend):
    """Console FCM backend for development environments."""

    def send_notification(self, device, **kwargs):
        print(f"Push to {device}\nPyFCM kwargs: {kwargs}\n")
        return {"name": "my/message/resource/:foobarbaz123"}


def get_fcm_backend():
    cls = app_settings.BACKEND_CLASS
    if cls is None:
        # default to console to avoid accidental push notifications
        return ConsoleFCMBackend()
    return import_string(cls)()
