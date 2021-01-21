from django.conf import settings


class AppSettings(object):
    def __init__(self, prefix, defaults):
        self.prefix = prefix
        self.defaults = defaults

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError(f"Invalid app setting: {attr}")
        return getattr(settings, f"{self.prefix}_{attr}", self.defaults[attr])


DEFAULTS = {
    # api key from Firebase for sending push messages
    "FCM_API_KEY": None,
    # allow customisation of how messages are actually sent
    "FCM_BACKEND_CLASS": None,
}


app_settings = AppSettings("DEVICES", DEFAULTS)
