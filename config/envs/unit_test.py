import base64
from os import getenv

from config.envs.default import DefaultConfig
from fsd_utils import configclass


@configclass
class UnitTestConfig(DefaultConfig):
    DefaultConfig.TALISMAN_SETTINGS["force_https"] = False
    USE_LOCAL_DATA = True
    FSD_USER_TOKEN_COOKIE_NAME = "fsd_user_token"
    AUTHENTICATOR_HOST = getenv("AUTHENTICATOR_HOST", "authenticator")
    SSO_LOGIN_URL = AUTHENTICATOR_HOST + "/sso/login"
    SSO_LOGOUT_URL = AUTHENTICATOR_HOST + "/sso/logout"

    # RSA 256 KEYS
    RSA256_PRIVATE_KEY_BASE64 = getenv("RSA256_PRIVATE_KEY_BASE64")
    if RSA256_PRIVATE_KEY_BASE64:
        RSA256_PRIVATE_KEY = base64.b64decode(
            RSA256_PRIVATE_KEY_BASE64
        ).decode()
    if not hasattr(DefaultConfig, "RSA256_PRIVATE_KEY"):
        _test_private_key_path = (
            DefaultConfig.FLASK_ROOT + "/tests/keys/rsa256/private.pem"
        )
        with open(_test_private_key_path, mode="rb") as private_key_file:
            RSA256_PRIVATE_KEY = private_key_file.read()

    RSA256_PUBLIC_KEY_BASE64 = getenv("RSA256_PUBLIC_KEY_BASE64")
    if RSA256_PUBLIC_KEY_BASE64:
        RSA256_PUBLIC_KEY = base64.b64decode(RSA256_PUBLIC_KEY_BASE64).decode()
    if not hasattr(DefaultConfig, "RSA256_PUBLIC_KEY"):
        _test_public_key_path = (
            DefaultConfig.FLASK_ROOT + "/tests/keys/rsa256/public.pem"
        )
        with open(_test_public_key_path, mode="rb") as public_key_file:
            RSA256_PUBLIC_KEY = public_key_file.read()
