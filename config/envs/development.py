import logging

from config.envs.default import DefaultConfig
from fsd_utils import configclass


@configclass
class DevelopmentConfig(DefaultConfig):

    # for local testing with flask run and USE_LOCAL_DATA = True:
    USE_LOCAL_DATA = True
    FSD_LOG_LEVEL = logging.INFO
    FUND_STORE_API_HOST = "fund_store"
    ASSESSMENT_STORE_API_HOST = "assessment_store"
    APPLICATION_STORE_API_HOST = "application_store"

    # FUND_STORE_API_HOST = "https://funding-service-design-fund-store-dev.london.cloudapps.digital" # noqa
    # ASSESSMENT_STORE_API_HOST = "https://funding-service-design-assessment-store-dev.london.cloudapps.digital" # noqa

    # for local dev/test use with flask run and USE_LOCAL_DATA = False:
    # FUND_STORE_API_HOST = (  # change in fund store repo and adjust here accordingly # noqa
    #     "http://127.0.0.1:5002"
    # )
    # ASSESSMENT_STORE_API_HOST = (  # change in assessment store repo and adjust here accordingly # noqa
    #     "http://127.0.0.1:5001"
    # )
