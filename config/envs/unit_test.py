import base64
from os import getenv

from fsd_utils import configclass

from config.envs.default import DefaultConfig


@configclass
class UnitTestConfig(DefaultConfig):
    DefaultConfig.TALISMAN_SETTINGS["force_https"] = False
    FSD_USER_TOKEN_COOKIE_NAME = "fsd_user_token"
    WTF_CSRF_ENABLED = False

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

    SHOW_ALL_ROUNDS = True
