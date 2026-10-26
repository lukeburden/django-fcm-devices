from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import pytest


PROJECT_ID = "foobarbaz123"


@pytest.fixture(scope="session")
def service_account_info():
    """
    Fake service account info, with a key generated per test run so that
    google-auth can load credentials and sign token requests for real.
    """
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return {
        "project_id": PROJECT_ID,
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_email": "firebase-notarealserviceaccount.gserviceaccount.com",
        "private_key": private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode(),
    }


@pytest.fixture(autouse=True)
def fcm_settings(settings, service_account_info):
    settings.FCM_DEVICES_GOOGLE_SERVICE_ACCOUNT_INFO = service_account_info
