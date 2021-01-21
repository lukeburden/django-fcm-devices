from django.urls import include

from rest_framework.routers import SimpleRouter

from fcm_devices.api.drf.views import DeviceViewSet


router = SimpleRouter()
router.register("devices", DeviceViewSet, basename="devices")


try:
    from django.urls import path

    urlpatterns = [path("", include(router.urls))]

except ImportError:
    from django.conf.urls import url

    urlpatterns = [url("", include(router.urls))]
