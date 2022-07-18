import os
from pathlib import Path

from fsd_utils import CommonConfig
from fsd_utils import configclass


@configclass
class DefaultConfig:

    # ---------------
    #  General App Config
    # ---------------

    SECRET_KEY = CommonConfig.SECRET_KEY
    SESSION_COOKIE_NAME = CommonConfig.SESSION_COOKIE_NAME
    FLASK_ROOT = str(Path(__file__).parent.parent.parent)
    FLASK_ENV = CommonConfig.FLASK_ENV

    FORCE_HTTPS = CommonConfig.FORCE_HTTPS
    FSD_LOG_LEVEL = CommonConfig.FSD_LOG_LEVEL

    STATIC_FOLDER = "app/static/dist"
    STATIC_URL_PATH = "/assets"
    TEMPLATES_FOLDER = "templates"
    LOCAL_SERVICE_NAME = "local_flask"
    ASSESSMENT_HUB_ROUTE = "/assess"

    """
    External APIs
    """
    # Fund Store Endpoints
    FUNDS_ENDPOINT = CommonConfig.FUNDS_ENDPOINT
    FUND_ENDPOINT = CommonConfig.FUND_ENDPOINT

    # Round Store Endpoints

    ROUNDS_ENDPOINT = CommonConfig.ROUNDS_ENDPOINT
    ROUND_ENDPOINT = CommonConfig.ROUND_ENDPOINT

    # Application Store Endpoints
    APPLICATION_ENDPOINT = CommonConfig.APPLICATION_ENDPOINT
    APPLICATION_STATUS_ENDPOINT = CommonConfig.APPLICATION_STATUS_ENDPOINT
    APPLICATION_SEARCH_ENDPOINT = CommonConfig.APPLICATION_SEARCH_ENDPOINT

    #Assesment store endpoints
    ASSESSMENT_STORE_API_HOST = os.environ.get("ASSESSMENT_STORE_API_HOST") or "ASSESSMENT_STORE_API_HOST"

    ASSESSMENT_SCORE_JUST_ENDPOINT = ASSESSMENT_STORE_API_HOST+"/assessments/{assessment_id}/sub_criterias/{sub_criteria_id}/scores"

    """
    Assets
    """
    ASSETS_DEBUG = False
    ASSETS_AUTO_BUILD = True

    """
    APIs Config
    """
    TEST_FUND_STORE_API_HOST = "fund_store"
    TEST_ROUND_STORE_API_HOST = "round_store"
    TEST_APPLICATION_STORE_API_HOST = "application_store"
    TEST_ASSESSMENT_STORE_API_HOST = "assessment_store"

    FUND_STORE_API_HOST = CommonConfig.FUND_STORE_API_HOST
    APPLICATION_STORE_API_HOST = CommonConfig.APPLICATION_STORE_API_HOST

    APPLICATION_STORE_API_HOST_PUBLIC = (
        os.environ.get("APPLICATION_STORE_API_HOST_PUBLIC")
        or os.environ.get("APPLICATION_STORE_API_HOST")
        or "/api/" + CommonConfig.TEST_APPLICATION_STORE_API_HOST
    )

    TALISMAN_SETTINGS = CommonConfig.TALISMAN_SETTINGS
