from django.urls import reverse

from model_bakery import baker
import pytest

from ..serializers import DeviceSerializer


@pytest.mark.django_db
def test_device_serializer_output():
    device = baker.make("fcm_devices.Device")
    data = DeviceSerializer(device).data
    assert data == {
        "id": device.id,
        "name": device.name,
        "active": device.active,
        "type": device.type,
        "token": device.token,
    }


@pytest.mark.django_db
def test_create_device_not_authenticated(api_client):
    response = api_client.post(
        reverse("devices-list"),
        {
            "name": "Steve's iBlackberry",
            "active": True,
            "type": "ios",
            "token": "iamalovelytokenindeed",
        },
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_create_device(api_client):
    user = baker.make("auth.User")
    api_client.force_authenticate(user)
    response = api_client.post(
        reverse("devices-list"),
        {
            "name": "Steve's iBlackberry",
            "active": True,
            "type": "ios",
            "token": "iamalovelytokenindeed",
        },
    )
    assert response.status_code == 201
    device = user.devices.first()
    assert response.data == DeviceSerializer(device).data


@pytest.mark.django_db
def test_create_device_duplicate(api_client):
    """
    Should not be possible to create duplicates as if there
    is a conflict the create will be commuted to an update.
    """
    device = baker.make("fcm_devices.Device")
    api_client.force_authenticate(device.user)
    response = api_client.post(
        reverse("devices-list"),
        {
            "name": "Steve's iBlackberry",
            "active": True,
            "type": "ios",
            "token": device.token,
        },
    )
    assert response.status_code == 201
    new_device = device.user.devices.last()
    assert new_device == device
