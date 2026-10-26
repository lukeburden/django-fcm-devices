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
    # from firebase service account file, found at
    # https://console.firebase.google.com/u/0/project/_/settings/serviceaccounts/adminsdk
    "GOOGLE_SERVICE_ACCOUNT_INFO": None,
    # allow customisation of how messages are actually sent
    "BACKEND_CLASS": None,
}


app_settings = AppSettings("FCM_DEVICES", DEFAULTS)
