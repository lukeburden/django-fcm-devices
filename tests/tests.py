import json

from django.contrib.messages import get_messages
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
from fcm_devices.models import Device

from .conftest import PROJECT_ID


@pytest.fixture()
def api_client():
    return APIClient()


# The internal URL hit by PyFCM to send a message
fcm_endpoint = f"{FCMNotification.FCM_END_POINT_BASE}/{PROJECT_ID}/messages:send"
# Oauth token refresh call
mock_token_response = {
    "access_token": "notarealtoken",
}
# tests for service logic

success_response = {"name": "projects/foobarbaz123/messages/0:1500415314455276"}


@pytest.mark.django_db
def test_update_or_create_device_create(mocker):
    user = baker.make("auth.User")
    assert Device.objects.count() == 0
    device_created_signal = mocker.patch(
        "fcm_devices.service.signals.device_created.send"
    )
    device_updated_signal = mocker.patch(
        "fcm_devices.service.signals.device_updated.send"
    )
    device, created = service.update_or_create_device(
        user=user,
        token="iamfcmroar",
        active=True,
        _type=Device.types.android,
        name="Pixel 2",
    )
    assert Device.objects.count() == 1
    assert created
    device_created_signal.assert_called_once_with(sender=Device, device=device)
    assert not device_updated_signal.called


@pytest.mark.django_db
def test_update_or_create_device_update(mocker):
    user = baker.make("auth.User")
    device = Device.objects.create(
        user=user,
        token="iamfcmroar",
        active=True,
        type=Device.types.android,
        name="Pixel 2",
    )
    initial_updated_at = device.updated_at
    assert Device.objects.count() == 1
    device_created_signal = mocker.patch(
        "fcm_devices.service.signals.device_created.send"
    )
    device_updated_signal = mocker.patch(
        "fcm_devices.service.signals.device_updated.send"
    )
    device, created = service.update_or_create_device(
        user=user,
        token="iamfcmroar",
        active=False,
        _type=Device.types.android,
        name="Pixel 2",
    )
    assert Device.objects.count() == 1
    assert not device.active
    assert not created
    assert device.updated_at > initial_updated_at
    device_updated_signal.assert_called_once_with(sender=Device, device=device)
    assert not device_created_signal.called


@pytest.mark.django_db
def test_device_model_str(mocker):
    user = baker.make("auth.User", first_name="Ringo")
    device = Device.objects.create(
        user=user,
        token="iamfcmroar",
        active=True,
        type=Device.types.android,
        name="Pixel 2",
    )
    assert str(device) == f"{user} on android w/ token iamfcmroar..."


@responses.activate
@pytest.mark.django_db
@override_settings(FCM_DEVICES_BACKEND_CLASS="fcm_devices.fcm.FCMBackend")
def test_send_notification(api_client):
    responses.add(
        responses.Response(
            method="POST",
            url=fcm_endpoint,
            json=success_response,
            status=200,
        )
    )
    responses.add(
        responses.Response(
            method="POST",
            url="https://oauth2.googleapis.com/token",
            json=mock_token_response,
        )
    )
    device = baker.make("fcm_devices.Device", active=True)
    response = service.send_notification(
        device, notification_title="Test title", notification_body="Test content"
    )
    assert response == success_response
    device.refresh_from_db()
    assert device.active


@responses.activate
@pytest.mark.django_db
@override_settings(FCM_DEVICES_BACKEND_CLASS="fcm_devices.fcm.FCMBackend")
def test_send_notification_invalid_device_unregistered(api_client, mocker):
    responses.add(
        responses.Response(
            method="POST",
            url=fcm_endpoint,
            status=404,
        )
    )
    responses.add(
        responses.Response(
            method="POST",
            url="https://oauth2.googleapis.com/token",
            json=mock_token_response,
        )
    )
    device = baker.make("fcm_devices.Device", active=True)
    initial_updated_at = device.updated_at
    device_updated_signal = mocker.patch(
        "fcm_devices.service.signals.device_updated.send"
    )
    service.send_notification(
        device, notification_title="Test title", notification_body="Test content"
    )

    device.refresh_from_db()
    assert not device.active
    assert device.updated_at > initial_updated_at
    device_updated_signal.assert_called_once_with(sender=Device, device=device)


@responses.activate
@pytest.mark.django_db
@override_settings(FCM_DEVICES_BACKEND_CLASS="fcm_devices.fcm.FCMBackend")
def test_send_notification_invalid_device_mismatch(api_client, mocker):
    responses.add(
        responses.Response(
            method="POST",
            url=fcm_endpoint,
            status=403,
        )
    )
    responses.add(
        responses.Response(
            method="POST",
            url="https://oauth2.googleapis.com/token",
            json=mock_token_response,
        )
    )
    device = baker.make("fcm_devices.Device", active=True)
    initial_updated_at = device.updated_at
    device_updated_signal = mocker.patch(
        "fcm_devices.service.signals.device_updated.send"
    )
    with pytest.raises(ImproperlyConfigured) as e:
        service.send_notification(
            device, notification_title="Test title", notification_body="Test content"
        )

    assert e.value.args[0] == (
        "The authenticated sender ID is different from the sender ID"
        " of the registration token."
    )

    device.refresh_from_db()
    assert not device.active
    assert device.updated_at > initial_updated_at
    device_updated_signal.assert_called_once_with(sender=Device, device=device)


@responses.activate
@pytest.mark.django_db
@override_settings(FCM_DEVICES_BACKEND_CLASS="fcm_devices.fcm.FCMBackend")
def test_send_notification_config_error(api_client, mocker, settings):
    settings.FCM_DEVICES_GOOGLE_SERVICE_ACCOUNT_INFO = {
        **settings.FCM_DEVICES_GOOGLE_SERVICE_ACCOUNT_INFO,
        "project_id": None,
    }
    responses.add(
        responses.Response(
            method="POST",
            url=fcm_endpoint,
            status=403,
        )
    )
    responses.add(
        responses.Response(
            method="POST",
            url="https://oauth2.googleapis.com/token",
            json=mock_token_response,
        )
    )
    device = baker.make("fcm_devices.Device", active=True)
    device_updated_signal = mocker.patch(
        "fcm_devices.service.signals.device_updated.send"
    )
    with pytest.raises(ImproperlyConfigured) as e:
        service.send_notification(
            device, notification_title="Test title", notification_body="Test content"
        )

    assert e.value.args[0] == ("GOOGLE_SERVICE_ACCOUNT_INFO must specify a project_id.")

    # device should not be deactivated; since it's a recoverable error we do not
    # need to purge the tokens, we just need to fix the config
    device.refresh_from_db()
    assert device.active
    assert not device_updated_signal.called


@pytest.mark.django_db
def test_send_notification_to_user_has_multiple_devices(mocker):
    user = baker.make("auth.User")
    active_device = baker.make("fcm_devices.Device", user=user, active=True)
    second_active_device = baker.make("fcm_devices.Device", user=user, active=True)
    baker.make("fcm_devices.Device", user=user, active=False)
    mocked_send_notification = mocker.patch("fcm_devices.service.send_notification")
    service.send_notification_to_user(
        user, notification_title="Test title", notification_body="Test content"
    )
    assert mocked_send_notification.call_count == 2
    mocked_send_notification.assert_any_call(
        active_device, notification_body="Test content", notification_title="Test title"
    )
    mocked_send_notification.assert_any_call(
        second_active_device,
        notification_body="Test content",
        notification_title="Test title",
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


# test admin send action


@pytest.mark.django_db
@responses.activate
@override_settings(FCM_DEVICES_BACKEND_CLASS="fcm_devices.fcm.FCMBackend")
def test_send_test_notification_action(client, mocker):
    responses.add(
        responses.Response(
            method="POST",
            url=fcm_endpoint,
            json=success_response,
            status=200,
        )
    )
    responses.add(
        responses.Response(
            method="POST",
            url="https://oauth2.googleapis.com/token",
            json=mock_token_response,
        )
    )
    device = baker.make(
        "fcm_devices.Device", user__is_staff=True, user__is_superuser=True
    )

    client.force_login(device.user)

    send_url = reverse("admin:fcm_devices_device_changelist")
    data = {
        "action": "send_notification",
        "select_across": "0",
        "index": "0",
        "_selected_action": device.id,
    }

    response = client.post(send_url, data=data)

    assert len(responses.calls) == 2
    assert response.status_code == 302
    assert json.loads(responses.calls[1].response.text) == success_response


@pytest.mark.django_db
@responses.activate
@override_settings(FCM_DEVICES_BACKEND_CLASS="fcm_devices.fcm.FCMBackend")
def test_send_test_notification_action_errors(client):
    responses.add(
        responses.Response(
            method="POST",
            url=fcm_endpoint,
            status=404,
        )
    )
    responses.add(
        responses.Response(
            method="POST",
            url=fcm_endpoint,
            status=403,
        )
    )
    responses.add(
        responses.Response(
            method="POST",
            url="https://oauth2.googleapis.com/token",
            json=mock_token_response,
        )
    )
    admin_user = baker.make("auth.User", is_staff=True, is_superuser=True)
    unregistered = baker.make("fcm_devices.Device", active=True)
    mismatched = baker.make("fcm_devices.Device", active=True)

    client.force_login(admin_user)

    response = client.post(
        reverse("admin:fcm_devices_device_changelist"),
        data={
            "action": "send_notification",
            "select_across": "0",
            "index": "0",
            "_selected_action": [unregistered.id, mismatched.id],
        },
    )

    assert response.status_code == 302
    messages = [str(m) for m in get_messages(response.wsgi_request)]
    assert messages == [
        "2 notifications hit errors: "
        "{'FCMNotRegisteredError': 1, 'ImproperlyConfigured': 1}"
    ]
    unregistered.refresh_from_db()
    mismatched.refresh_from_db()
    assert not unregistered.active
    assert not mismatched.active
