import base64
import logging
from os import getenv

from config.envs.default import DefaultConfig
from fsd_utils import configclass


@configclass
class DevelopmentConfig(DefaultConfig):

    # for local testing with flask run and USE_LOCAL_DATA = True:
    # USE_LOCAL_DATA = True
    # FSD_LOG_LEVEL = logging.INFO
    # FUND_STORE_API_HOST = "fund_store"
    # ASSESSMENT_STORE_API_HOST = "assessment_store"
    # APPLICATION_STORE_API_HOST = "application_store"

    # FUND_STORE_API_HOST = "https://funding-service-design-fund-store-dev.london.cloudapps.digital" # noqa
    # ASSESSMENT_STORE_API_HOST = "https://funding-service-design-assessment-store-dev.london.cloudapps.digital" # noqa

    # for testing with docker runner:
    USE_LOCAL_DATA = False
    FSD_LOG_LEVEL = logging.INFO
    FSD_USER_TOKEN_COOKIE_NAME = "fsd_user_token"
    AUTHENTICATOR_HOST = getenv("AUTHENTICATOR_HOST", "authenticator")
    SSO_LOGIN_URL = AUTHENTICATOR_HOST + "/sso/login"
    SSO_LOGOUT_URL = AUTHENTICATOR_HOST + "/sso/logout"
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
