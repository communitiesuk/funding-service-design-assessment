from config.envs.default import DefaultConfig
from fsd_utils import configclass


@configclass
class DevelopmentConfig(DefaultConfig):
    ASSESSMENT_SCORES_ENDPOINT = (
        DefaultConfig.ASSESSMENT_STORE_API_HOST + "/score"
    )

    # USE_LOCAL_DATA = True
    USE_LOCAL_DATA = False

    # FUND_STORE_API_HOST = "https://funding-service-design-fund-store-dev.london.cloudapps.digital" # noqa
    # ASSESSMENT_STORE_API_HOST = "https://funding-service-design-assessment-store-dev.london.cloudapps.digital" # noqa

    # for local dev/test use with flask run and USE_LOCAL_DATA = False:
    FUND_STORE_API_HOST = (  # change in fund store repo and adjust here accordingly # noqa
        "http://127.0.0.1:5002"
    )
    ASSESSMENT_STORE_API_HOST = (  # change in assessment store repo and adjust here accordingly # noqa
        "http://127.0.0.1:5001"
    )
    ASSESSMENT_SCORES_ENDPOINT = ASSESSMENT_STORE_API_HOST + "/score"
