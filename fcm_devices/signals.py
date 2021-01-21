from django.dispatch import Signal


# fired any time a device is created
device_created = Signal(providing_args=["device"])


# fired any time a device is updated
device_updated = Signal(providing_args=["device"])
