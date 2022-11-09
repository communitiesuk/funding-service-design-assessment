from os import getenv
from pathlib import Path

from distutils.util import strtobool
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
    APIs Config
    """
    FUND_STORE_API_HOST = CommonConfig.FUND_STORE_API_HOST
    APPLICATION_STORE_API_HOST = CommonConfig.APPLICATION_STORE_API_HOST
    ASSESSMENT_STORE_API_HOST = CommonConfig.ASSESSMENT_STORE_API_HOST

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

    # Assesment store endpoints
    ASSESSMENT_STORE_API_HOST = CommonConfig.ASSESSMENT_STORE_API_HOST
    APPLICATION_OVERVIEW_ENDPOINT = (
        "/application_overviews/{fund_id}/{round_id}"
    )

    ASSESSMENT_SCORE_JUST_ENDPOINT = (
        ASSESSMENT_STORE_API_HOST
        + "/assessments/{assessment_id}/sub_criterias/{sub_criteria_id}/scores"
    )

    """
    Assets
    """
    ASSETS_DEBUG = False
    ASSETS_AUTO_BUILD = True

    TALISMAN_SETTINGS = CommonConfig.TALISMAN_SETTINGS

    # TODO move into common config
    COF_FUND_ID = "47aef2f5-3fcb-4d45-acb5-f0152b5f03c4"
    COF_ROUND2_ID = "c603d114-5364-4474-a0c4-c41cbf4d3bbd"

    USE_LOCAL_DATA = strtobool(getenv("USE_LOCAL_DATA", "False"))
