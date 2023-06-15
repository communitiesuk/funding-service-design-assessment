import base64
import logging
from os import getenv

from config.envs.default import DefaultConfig
from fsd_utils import CommonConfig  # noqa
from fsd_utils import configclass


@configclass
class DevelopmentConfig(DefaultConfig):

    # RSA 256 KEYS
    if not hasattr(DefaultConfig, "RSA256_PUBLIC_KEY"):
        _test_public_key_path = (
            DefaultConfig.FLASK_ROOT + "/tests/keys/rsa256/public.pem"
        )
        with open(_test_public_key_path, mode="rb") as public_key_file:
            RSA256_PUBLIC_KEY = public_key_file.read()

    # for testing with docker runner:
    FSD_LOG_LEVEL = logging.INFO
    FSD_USER_TOKEN_COOKIE_NAME = "fsd_user_token"
    AUTHENTICATOR_HOST = getenv("AUTHENTICATOR_HOST", "https://authenticator")
    SSO_LOGIN_URL = AUTHENTICATOR_HOST + "/sso/login"
    SSO_LOGOUT_URL = AUTHENTICATOR_HOST + "/sso/logout"

    DEBUG_USER_ON = True  # Set to True to use DEBUG user
    SHOW_ALL_ROUNDS = True  # Set to True to show all rounds

    DEBUG_USER_ROLE = getenv(
        "DEBUG_USER_ROLE", "COMMENTER" if DEBUG_USER_ON else ""
    )

    # CUSTOM_ROLE = "COF_WALES"
    # CUSTOM_ROLE = "COF_SCOTLAND"
    # CUSTOM_ROLE = "COF_ENGLAND"
    # CUSTOM_ROLE = "COF_NORTHERNIRELAND"

    DEBUG_USER = {
        "full_name": "Development User",
        "email": "dev@example.com",
        "roles": [
            "LEAD_ASSESSOR",
            "COF_ENGLAND",
        ],  # should only be able to access english apps, 403 all others
        "highest_role": "LEAD_ASSESSOR",
    }

    # RSA 256 KEYS
    RSA256_PUBLIC_KEY_BASE64 = getenv("RSA256_PUBLIC_KEY_BASE64")
    if RSA256_PUBLIC_KEY_BASE64:
        RSA256_PUBLIC_KEY = base64.b64decode(RSA256_PUBLIC_KEY_BASE64).decode()
    if not hasattr(DefaultConfig, "RSA256_PUBLIC_KEY"):
        _test_public_key_path = (
            DefaultConfig.FLASK_ROOT + "/tests/keys/rsa256/public.pem"
        )
        with open(_test_public_key_path, mode="rb") as public_key_file:
            RSA256_PUBLIC_KEY = public_key_file.read()

    AWS_ACCESS_KEY_ID = getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = getenv("AWS_SECRET_ACCESS_KEY")
    AWS_BUCKET_NAME = getenv("AWS_BUCKET_NAME")
    AWS_REGION = "eu-west-2"
