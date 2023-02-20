import base64
import logging
from os import getenv

from config.envs.default import DefaultConfig
from fsd_utils import CommonConfig  # noqa
from fsd_utils import configclass
import redis

@configclass
class DevelopmentConfig(DefaultConfig):

    # RSA 256 KEYS
    if not hasattr(DefaultConfig, "RSA256_PUBLIC_KEY"):
        _test_public_key_path = (
            DefaultConfig.FLASK_ROOT + "/tests/keys/rsa256/public.pem"
        )
        with open(_test_public_key_path, mode="rb") as public_key_file:
            RSA256_PUBLIC_KEY = public_key_file.read()

    # for local testing with flask run and USE_LOCAL_DATA = True:
    # USE_LOCAL_DATA = True
    # if USE_LOCAL_DATA:
    #     ACCOUNT_STORE_API_HOST = CommonConfig.TEST_ACCOUNT_STORE_API_HOST
    #     APPLICATION_STORE_API_HOST = CommonConfig.TEST_APPLICATION_STORE_API_HOST # noqa
    #     ASSESSMENT_STORE_API_HOST = CommonConfig.TEST_ASSESSMENT_STORE_API_HOST # noqa
    #     FUND_STORE_API_HOST = CommonConfig.TEST_FUND_STORE_API_HOST

    # for testing with docker runner:
    FSD_LOG_LEVEL = logging.INFO
    FSD_USER_TOKEN_COOKIE_NAME = "fsd_user_token"
    AUTHENTICATOR_HOST = getenv("AUTHENTICATOR_HOST", "https://authenticator")
    SSO_LOGIN_URL = AUTHENTICATOR_HOST + "/sso/login"
    SSO_LOGOUT_URL = AUTHENTICATOR_HOST + "/sso/logout"

    DEBUG_USER_ON = True  # Set to True to use DEBUG user

    DEBUG_USER_ROLE = getenv(
        "DEBUG_USER_ROLE", "LEAD_ASSESSOR" if DEBUG_USER_ON else ""
    )

    DEBUG_USER = {
        "full_name": "Development User",
        "email": "dev@example.com",
        "roles": {
            "LEAD_ASSESSOR": ["LEAD_ASSESSOR", "ASSESSOR", "COMMENTER"],
            "ASSESSOR": ["ASSESSOR", "COMMENTER"],
            "COMMENTER": ["COMMENTER"],
        }.get(DEBUG_USER_ROLE),
        "highest_role": DEBUG_USER_ROLE,
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

    # Redis

    REDIS_INSTANCE_URI = getenv("REDIS_INSTANCE_URI", "redis://localhost:6379")
    REDIS_MLINKS_URL = f"{REDIS_INSTANCE_URI}/0"
    REDIS_SESSIONS_URL = f"{REDIS_INSTANCE_URI}/1"
    SESSION_REDIS = redis.from_url(REDIS_SESSIONS_URL)