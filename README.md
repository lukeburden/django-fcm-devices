# Register devices and send push notifications via FCM from your Django app

[![](https://img.shields.io/pypi/v/django-fcm-devices.svg)](https://pypi.python.org/pypi/django-fcm-devices/)
[![](https://img.shields.io/badge/license-MIT-blue.svg)](https://pypi.python.org/pypi/django-fcm-devices/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![Codecov](https://codecov.io/gh/lukeburden/django-fcm-devices/branch/master/graph/badge.svg)](https://codecov.io/gh/lukeburden/django-fcm-devices)
[![CircleCI](https://circleci.com/gh/lukeburden/django-fcm-devices.svg?style=svg)](https://circleci.com/gh/lukeburden/django-fcm-devices)


## django-fcm-devices

`django-fcm-devices` is a Django app that facilitates the registration of devices' FCM tokens and sending of push notifications to those devices.

The approach taken in this library is different to other libraries, in that it aims to be super simple and well tested.


### Installation ####

pip install django-fcm-devices


### Configuration ###

You need to configure your FCM API key by adding to your settings:

- `DEVICES_FCM_API_KEY` your FCM API key.

You can optionally subclass the `FCMBackend` to add your own behaviour using the following setting and dot notation:

- `DEVICES_FCM_BACKEND_CLASS` 


### Usage ###

Todo: describe API exposure and behaviour

Todo: show use without API usage


## Contribute

`django-fcm-devices` supports a variety of Python and Django versions. It's best if you test each one of these before committing. Our [Circle CI Integration](https://circleci.com) will test these when you push but knowing before you commit prevents from having to do a lot of extra commits to get the build to pass.

### Environment Setup

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
pyenv virtualenv devices 3.8.1
pyenv shell devices 3.6.10 3.7.6
pip install detox
```

To run the test suite:

```
$ detox
```
