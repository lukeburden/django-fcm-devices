from django.contrib import admin
from django.urls import include, path

from rest_framework.routers import SimpleRouter

from fcm_devices.api.drf.views import DeviceViewSet


router = SimpleRouter()
router.register("devices", DeviceViewSet, basename="devices")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
]
