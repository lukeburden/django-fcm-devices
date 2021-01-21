from django.conf import settings
from django.db import models
from django.utils import timezone

from konst import Constant, Constants
from konst.models.fields import ConstantChoiceCharField


class Device(models.Model):
    """
    Store info about a specific instance of an app on a specific device.

    A registration token is unique to an install (in the case of a mobile app)
    on a specific device. Different users could, in theory, share a registration
    token.

    To allow us to send notifications for the right user to a device we enforce
    uniqueness on the basis of user and token value and let the user manipulate
    the `active` boolean. For example, they might toggle it to False on logout.

    This uniqueness constraint also lets us use `update_or_create` et al and
    create a low-friction API.
    """

    id = models.BigAutoField(primary_key=True)

    types = Constants(
        Constant(ios="ios"), Constant(android="android"), Constant(web="web")
    )

    name = models.TextField(
        max_length=1024,
        help_text="Name provided by users for easy recognition of the device",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="devices"
    )
    active = models.BooleanField(
        default=True,
        help_text="FCM or the user may indicated if the token is valid or not",
    )
    type = ConstantChoiceCharField(constants=types, max_length=30)
    token = models.TextField(help_text="The FCM registration token value")

    # some timestamps for our info
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("user", "token")

    def __str__(self):
        return f"{self.user} on {self.type} w/ token {self.token[:10]}..."
