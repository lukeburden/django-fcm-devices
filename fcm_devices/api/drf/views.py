from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from ...models import Device
from .serializers import DeviceSerializer


class DeviceViewSet(viewsets.ModelViewSet):
    """
    Allow a user to register and manage FCM tokens for their devices.

    This API sets out to allow client code to be as simple as possible.
    To do this, it bends the rules of REST a little and will commute a
    POST to an update (normally would be a PATCH) if

    This means that client code can have a function to generate the state
    of its current push registration and simply POST that to this API
    on both login and logout.
    """

    permission_classes = (IsAuthenticated,)
    http_method_names = ["post"]
    serializer_class = DeviceSerializer

    def get_queryset(self, *args, **kwargs):
        return Device.objects.filter(user=self.request.user)
