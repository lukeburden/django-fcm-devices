from django.core.exceptions import ImproperlyConfigured
from django.test import override_settings
from django.urls import reverse

from model_bakery import baker
from pyfcm.fcm import FCMNotification
import pytest
import responses
from rest_framework.test import APIClient

from fcm_devices import service
from fcm_devices.api.drf.serializers import DeviceSerializer


@pytest.fixture()
def api_client():
    return APIClient()


# tests for service logic

success_response = {
    "multicast_ids": [],
    "success": 1,
    "failure": 0,
    "canonical_ids": 0,
    "results": [],
    "topic_message_id": None,
}


unrecoverable_error_response = {
    "multicast_ids": [],
    "success": 0,
    "failure": 1,
    "canonical_ids": 0,
    "results": [{"error": "InvalidRegistration"}],
    "topic_message_id": None,
}


configuration_error_response = {
    "multicast_ids": [],
    "success": 0,
    "failure": 1,
    "canonical_ids": 0,
    "results": [{"error": "MismatchSenderId"}],
    "topic_message_id": None,
}


# TODO: add tests for update_or_create_device


@responses.activate
@pytest.mark.django_db
@override_settings(DEVICES_FCM_BACKEND_CLASS="fcm_devices.fcm.FCMBackend")
def test_send_notification(api_client):
    responses.add(
        responses.Response(
            method="POST",
            url=FCMNotification.FCM_END_POINT,
            match_querystring=False,
            json=success_response,
            status=200,
        )
    )
    device = baker.make("fcm_devices.Device", active=True)
    response = service.send_notification(
        device, title="Test title", body="Test content"
    )
    assert response == success_response
    device.refresh_from_db()
    assert device.active


@responses.activate
@pytest.mark.django_db
@override_settings(DEVICES_FCM_BACKEND_CLASS="fcm_devices.fcm.FCMBackend")
def test_send_notification_invalid_device(api_client):
    responses.add(
        responses.Response(
            method="POST",
            url=FCMNotification.FCM_END_POINT,
            match_querystring=False,
            json=unrecoverable_error_response,
            status=200,
        )
    )
    device = baker.make("fcm_devices.Device", active=True)
    response = service.send_notification(
        device, title="Test title", body="Test content"
    )
    assert response == unrecoverable_error_response
    device.refresh_from_db()
    assert not device.active


@responses.activate
@pytest.mark.django_db
@override_settings(DEVICES_FCM_BACKEND_CLASS="fcm_devices.fcm.FCMBackend")
def test_send_notification_config_error(api_client):
    responses.add(
        responses.Response(
            method="POST",
            url=FCMNotification.FCM_END_POINT,
            match_querystring=False,
            json=configuration_error_response,
            status=200,
        )
    )
    device = baker.make("fcm_devices.Device", active=True)
    with pytest.raises(ImproperlyConfigured) as e:
        service.send_notification(device, title="Test title", body="Test content")
        assert e.value == f"Uh o h device {device.id}: MismatchSenderId"

    # device should not be deactivated, as if it is a recoverable error we do not
    # need to purge the tokens, we just need to fix the config
    device.refresh_from_db()
    assert device.active


@pytest.mark.django_db
def test_send_notification_to_user_has_multiple_devices(mocker):
    user = baker.make("auth.User")
    active_device = baker.make("fcm_devices.Device", user=user, active=True)
    second_active_device = baker.make("fcm_devices.Device", user=user, active=True)
    baker.make("fcm_devices.Device", user=user, active=False)
    mocked_send_notification = mocker.patch("fcm_devices.service.send_notification")
    service.send_notification_to_user(user, title="Test title", body="Test content")
    assert mocked_send_notification.call_count == 2
    mocked_send_notification.assert_any_call(
        active_device, body="Test content", title="Test title"
    )
    mocked_send_notification.assert_any_call(
        second_active_device, body="Test content", title="Test title"
    )


# tests for API


@pytest.mark.django_db
def test_device_serializer_output():
    device = baker.make("fcm_devices.Device")
    data = DeviceSerializer(device).data
    assert data == {
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
    assert response.status_code == 403


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
