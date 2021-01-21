from . import signals
from .fcm import get_fcm_backend
from .models import Device


def update_or_create_device(user, token, active, _type, name):
    """
    Create or update a device and fire an appropriate signal
    for other apps to potentially use.
    """
    instance, created = Device.objects.update_or_create(
        user=user,
        token=token,
        defaults={
            "active": active,
            "type": _type,
            "name": name,
        },
    )
    if created:
        signals.device_created.send(sender=Device, device=instance)
    else:
        signals.device_updated.send(sender=Device, device=instance)
    return instance, created


def send_notification(device, **kwargs):
    """
    Send a push notification to a device.

    Note that kwargs are passed through to the backend which by default
    uses pyfcm, so you can check their docs for what you can include.
    """
    return get_fcm_backend().send_notification(device, **kwargs)


def send_notification_to_user(user, **kwargs):
    """
    Send a push notification to all active devices for a User.
    """
    devices = Device.objects.filter(user=user, active=True)
    for device in devices:
        send_notification(device, **kwargs)


# TODO: add functions for bulk sends, data messages, etc. For now
# if you need these, just subclass FCMBackend and hit it directly
