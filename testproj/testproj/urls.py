from django.contrib import admin
from django.urls import include, path

from rest_framework.routers import SimpleRouter

from fcm_devices.api.drf.views import DeviceViewSet


router = SimpleRouter()
router.register("devices", DeviceViewSet, basename="devices")

urlpatterns = [
    # path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path("admin/", admin.site.urls),
    path("", include(router.urls)),
]


# try:
#     from django.urls import path
#     urlpatterns = [path('', include(router.urls))]

# except ImportError:
#     from django.conf.urls import url
#     urlpatterns = [url('', include(router.urls))]
