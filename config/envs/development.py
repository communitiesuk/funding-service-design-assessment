import base64
import logging
from os import getenv

from fsd_utils import configclass

from config.envs.default import DefaultConfig


@configclass
class DevelopmentConfig(DefaultConfig):
    # RSA 256 KEYS
    if not hasattr(DefaultConfig, "RSA256_PUBLIC_KEY"):
        _test_public_key_path = DefaultConfig.FLASK_ROOT + "/tests/keys/rsa256/public.pem"
        with open(_test_public_key_path, mode="rb") as public_key_file:
            RSA256_PUBLIC_KEY = public_key_file.read()

    # for testing with docker runner:
    FSD_LOG_LEVEL = logging.INFO
    FSD_USER_TOKEN_COOKIE_NAME = "fsd_user_token"
    AUTHENTICATOR_HOST = getenv("AUTHENTICATOR_HOST", "https://authenticator")
    SSO_LOGIN_URL = AUTHENTICATOR_HOST + "/sso/login"
    SSO_LOGOUT_URL = AUTHENTICATOR_HOST + "/sso/logout"

    DEBUG_USER_ON = True  # Set to True to use DEBUG user

    DEBUG_USER_ROLE = "LEAD_ASSESSOR"
    DEBUG_USER = {
        "full_name": "Development User",
        "email": "dev@example.com",
        "roles": [
            "COF_LEAD_ASSESSOR",
            "COF_ASSESSOR",
            "COF_COMMENTER",
            "COF_ENGLAND",
            "COF_SCOTLAND",
            "COF_WALES",
            "COF_NORTHERNIRELAND",
            "NSTF_LEAD_ASSESSOR",
            "NSTF_ASSESSOR",
            "NSTF_COMMENTER",
            "CYP_LEAD_ASSESSOR",
            "CYP_ASSESSOR",
            "CYP_COMMENTER",
            "DPIF_LEAD_ASSESSOR",
            "DPIF_ASSESSOR",
            "DPIF_COMMENTER",
            "COF-EOI_LEAD_ASSESSOR",
            "COF-EOI_ASSESSOR",
            "COF-EOI_COMMENTER",
            "HSRA_LEAD_ASSESSOR",
            "HSRA_ASSESSOR",
            "HSRA_COMMENTER",
            "CTDF_LEAD_ASSESSOR",
            "CTDF_ASSESSOR",
        ],
        "highest_role_map": {
            "CTDF": DEBUG_USER_ROLE,
            "COF": DEBUG_USER_ROLE,
            "NSTF": DEBUG_USER_ROLE,
            "CYP": DEBUG_USER_ROLE,
            "DPIF": DEBUG_USER_ROLE,
            "COF-EOI": DEBUG_USER_ROLE,
            "HSRA": DEBUG_USER_ROLE,
        },
    }
    DEBUG_USER_ACCOUNT_ID = "00000000-0000-0000-0000-000000000000"

    # RSA 256 KEYS
    RSA256_PUBLIC_KEY_BASE64 = getenv("RSA256_PUBLIC_KEY_BASE64")
    if RSA256_PUBLIC_KEY_BASE64:
        RSA256_PUBLIC_KEY = base64.b64decode(RSA256_PUBLIC_KEY_BASE64).decode()
    if not hasattr(DefaultConfig, "RSA256_PUBLIC_KEY"):
        _test_public_key_path = DefaultConfig.FLASK_ROOT + "/tests/keys/rsa256/public.pem"
        with open(_test_public_key_path, mode="rb") as public_key_file:
            RSA256_PUBLIC_KEY = public_key_file.read()

    AWS_ACCESS_KEY_ID = getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = getenv("AWS_SECRET_ACCESS_KEY")
    AWS_BUCKET_NAME = getenv("AWS_BUCKET_NAME")
    AWS_REGION = "eu-west-2"

    FEATURE_CONFIG = {"TAGGING": True, "ASSESSMENT_ASSIGNMENT": True}
    ASSETS_AUTO_BUILD = True

    # LRU cache settings
    LRU_CACHE_TIME = 30  # in seconds
    SECRET_KEY = "dev"  # pragma: allowlist secret
