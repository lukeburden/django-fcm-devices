# Minimalistic FCM device registration for your Django app

[![](https://img.shields.io/pypi/v/django-fcm-devices.svg)](https://pypi.python.org/pypi/django-fcm-devices/)
[![](https://img.shields.io/badge/license-MIT-blue.svg)](https://pypi.python.org/pypi/django-fcm-devices/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![Codecov](https://codecov.io/gh/lukeburden/django-fcm-devices/branch/master/graph/badge.svg)](https://codecov.io/gh/lukeburden/django-fcm-devices)
[![CircleCI](https://circleci.com/gh/lukeburden/django-fcm-devices.svg?style=svg)](https://circleci.com/gh/lukeburden/django-fcm-devices)


## django-fcm-devices

`django-fcm-devices` takes a minimalistic and opinionated approach to letting your app register FCM tokens and receive push notifications.

It assumes you have an app (mobile, web, whatever!) and users who log into this app. It assumes you want to solely use FCM to send push notifications to those users. And it assumes you want the interaction between your apps and your backend to be as straight-forward as possible.

Before authoring this library, existing options were considered. They tend to provide APIs that are too expansive and brittle to allow the app code to be dead simple. They tend to make schema choices early on which are hard to tighten up later, resulting in further brittleness and race conditions.

That said, the top contenders - [django-push-notifications](https://github.com/jazzband/django-push-notifications) and [fcm-django](https://github.com/xtrinch/fcm-django) - are worth checking out and just may fit your specific use-case better. Personally, I've always found myself _wanting less_.

This library leverages the excellent [PyFCM](https://github.com/olucurious/PyFCM) to interact with Firebase once you've registered your devices.

This library uses [semantic versioning](https://semver.org/spec/v2.0.0.html) because no one likes surprise backward incompatible changes, right?


### Install ####

pip install django-fcm-devices


### Configure ###

You need to configure your FCM API key by adding to your settings:

- `FCM_DEVICES_API_KEY` your FCM API key.

You can optionally subclass the `FCMBackend` to add your own behaviour using the following setting and dot notation:

- `FCM_DEVICES_BACKEND_CLASS` 


### Use ###

#### Manage FCM tokens ####

When you get your device's FCM registration token in app, you simply need to POST it to the backend along with some extra data.

```
POST /v1/devices/

{
    "token": "<your FCM token value>",
    "name": "A string describing your device, ie - iPhone. Just descriptive.",
    "active": true,
    "type": "ios"
}
```

If you get a 201 response, the token is registered and that device should now be able to receive push notifications.

Next, your user might log out of your app on their device. They will still receive push notifications despite no longer being authenticated on the app. To prevent this (if you prefer!) before logging out, simply update the device such that it is no longer `active`:

```
POST /v1/devices/

{
    "token": "<your FCM token value>",
    "name": "Jimbo's iPhone",
    "active": false,
    "type": "ios"
}
```

If you receive a 201 response, those changes are persisted.

Notice how similar the create and update are? In fact, they're more or less the same. This is an idempotent endpoint, which is a little unusual but not forbidden for a POST request.

Note: use of PUT for this was considered, but typically PUT is used when the caller specifies the ID of the resource in the URL. This would logically be the registration ID, however it is not clear [whether or not FCM registration tokens are dependably URL-safe](https://stackoverflow.com/questions/12403628/is-there-a-gcm-registrationid-pattern/12502351#12502351) and I didn't want the added complexity of requiring callers to URL encode them.


#### Send push notifications ####

So you've had your app register a token - sending them a push is easy enough. This library provides some convenience functions, as follow:

```python
from django.contrib.auth.models import User

from fcm_devices.models import Device
from fcm_devices.service import send_notification, send_notification_to_user

device = Device.objects.get(user_id=123)  # get the device for the user you want to message

send_notification(device, title="An important push", body="Oh dear ..")

# or send it straight to all the user's devices
send_notification_to_user(User.objects.get(id=123), title="An important push", body="Oh dear ..")
```

These functions have the added bonus of processing sending errors and deactivating devices, so they should generally be used.

But what about bulk and data notifications, you ask? Well, easy does it tiger. We'll likely get there (or send along a PR?!) but in the meantime you can easily do this yourself by directly using [PyFCM](https://github.com/olucurious/PyFCM):

```python
from pyfcm import FCMNotification

from fcm_devices.models import Device
from fcm_devices.settings import app_settings

push_service = FCMNotification(api_key=app_settings.API_KEY)
data_message = {
    "Nick": "Mario",
    "body": "great match!",
    "Room": "PortugalVSDenmark"
}

device = Device.objects.get(user_id=123)  # get the device for the user you want to message

# To multiple devices
result = push_service.notify_multiple_devices(
    registration_ids=[device.token],
    message_body="Hullo there",
    data_message=data_message
)

# To a single device
result = push_service.notify_single_device(
    registration_id=device.token,
    message_body="Hullo there",
    data_message=data_message
)
```

#### A word on the circle of life (of an FCM token) ####

As you've now read, this library just lets you PUT tokens. It doesn't let you list your tokens or delete them yourself. This simplicity is only really OK due to the life-cycle of an FCM token.

When you get an FCM token, it is usually because you've just opened an app after installing it, restoring it or wiping its data. This token is specific to the very install of the application your using. Notably, it is not specific to the user logged into the application.

While that app installation remains intact, you can typically continue to use the token to notify that user.

Finally, when FCM attempts to deliver a message to the device and the app was uninstalled, FCM discards that message right away and invalidates the registration token. Future attempts to send a message to that device results in a NotRegistered error.

Assuming you're using the convenience methods this library provides, when a token is found to be invalid it will be marked with `active` set to false. This typically is the end of that token's life - you might want to periodically purge inactive tokens if your space conscious.


### Contribute ###

Spot a bug or something that needs a test? Contributions are very welcome, but bear in mind that this library aims to be minimalistic and somewhat opinionated in its approach and that larger feature additions should likely be put in dependent but separate apps.


#### Run the tests ####

In order to easily test on all these Pythons and run the exact same thing that CI will execute you'll want to setup [pyenv](https://github.com/yyuu/pyenv) and install the Python versions outlined in [tox.ini](https://github.com/lukeburden/django-fcm-devices/blob/master/tox.ini).

If you are on Mac OS X, it's recommended you use [brew](http://brew.sh/). After installing `brew` run:

```
$ brew install pyenv pyenv-virtualenv pyenv-virtualenvwrapper
```

Then:

```
pyenv install -s 3.6.10
pyenv install -s 3.7.6
pyenv install -s 3.8.1
pyenv install -s 3.9.1
pyenv virtualenv devices 3.8.1
pyenv shell devices 3.6.10 3.7.6 3.9.1
pip install tox
```

And to run the test suite:

```
$ tox
```


#### Submit a PR ####

Once you've fixed your bug and added a regression test or two, feel free to submit a pull request and I'll take a look. Please be thorough in explaining what your PR aims to achieve.
