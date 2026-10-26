from django.dispatch import Signal


# fired any time a device is created, with a `device` kwarg
device_created = Signal()


# fired any time a device is updated, with a `device` kwarg
device_updated = Signal()
