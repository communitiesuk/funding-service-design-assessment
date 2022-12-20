import logging

from config.envs.default import DefaultConfig
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

    # for local testing with flask run and USE_LOCAL_DATA = True:
    USE_LOCAL_DATA = True
    FSD_LOG_LEVEL = logging.INFO
    # FUND_STORE_API_HOST = "fund_store"
    # ASSESSMENT_STORE_API_HOST = "assessment_store"
    # APPLICATION_STORE_API_HOST = "application_store"

    # FUND_STORE_API_HOST = "https://funding-service-design-fund-store-dev.london.cloudapps.digital" # noqa
    # ASSESSMENT_STORE_API_HOST = "https://funding-service-design-assessment-store-dev.london.cloudapps.digital" # noqa
