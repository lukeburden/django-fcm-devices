from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from ...models import Device
from .serializers import DeviceSerializer


class DeviceViewSet(viewsets.ModelViewSet):
    """
    Allow a user to manage FCM tokens for their devices.

    To allow client code to be ultra simple this API provides an idempotent
    POST endpoint.

    Client code can then not worry about previous tokens and simply update the
    backend with the latest token, name and state.

    ## POST ##

    ### Register an FCM device ###

    This will store the given device details against the current user.

        POST /v1/device/fcm
        {
            "name": <unicode>,
            "type": "ios" | "android" | "web",
            "token": <fcm token string>,
            "active": <boolean>
        }

    ### Updating an existing device ###

    To update an existing device you can simply POST the same token value again but
    with a change to the name or active state.

        POST v1/device/fcm
        {
            "name": <unicode>,
            "type": "ios" | "android" | "web",
            "token": <fcm token string>,
            "active": <boolean>
        }

    """

    permission_classes = (IsAuthenticated,)
    http_method_names = ["post"]
    serializer_class = DeviceSerializer

    def get_queryset(self, *args, **kwargs):
        return Device.objects.filter(user=self.request.user)
