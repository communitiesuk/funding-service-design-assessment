import base64
from os import environ
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

    # Authentication
    FSD_USER_TOKEN_COOKIE_NAME = "fsd_user_token"
    AUTHENTICATOR_HOST = environ.get("AUTHENTICATOR_HOST", "authenticator")
    FSD_USER_TOKEN_COOKIE_NAME = "fsd_user_token"
    # RSA 256 KEYS
    RSA256_PUBLIC_KEY_BASE64 = environ.get("RSA256_PUBLIC_KEY_BASE64")
    if RSA256_PUBLIC_KEY_BASE64:
        RSA256_PUBLIC_KEY = base64.b64decode(RSA256_PUBLIC_KEY_BASE64).decode()

    FORCE_HTTPS = CommonConfig.FORCE_HTTPS
    FSD_LOG_LEVEL = CommonConfig.FSD_LOG_LEVEL
    FSD_USER_TOKEN_COOKIE_NAME = "fsd_user_token"

    STATIC_FOLDER = "app/static/dist"
    STATIC_URL_PATH = "/assets"
    TEMPLATES_FOLDER = "templates"
    LOCAL_SERVICE_NAME = "local_flask"
    ASSESSMENT_HUB_ROUTE = "/assess"
    DASHBOARD_ROUTE = "/assess/assessor_dashboard"

    """
    Security
    """

    AUTHENTICATOR_HOST = getenv("AUTHENTICATOR_HOST", "https://authenticator")
    SSO_LOGIN_URL = AUTHENTICATOR_HOST + "/sso/login"
    SSO_LOGOUT_URL = AUTHENTICATOR_HOST + "/sso/logout"
    # RSA 256 KEYS
    RSA256_PUBLIC_KEY_BASE64 = getenv("RSA256_PUBLIC_KEY_BASE64")
    if RSA256_PUBLIC_KEY_BASE64:
        RSA256_PUBLIC_KEY = base64.b64decode(RSA256_PUBLIC_KEY_BASE64).decode()

    """
    APIs Config
    """
    FUND_STORE_API_HOST = CommonConfig.FUND_STORE_API_HOST
    APPLICATION_STORE_API_HOST = CommonConfig.APPLICATION_STORE_API_HOST
    ASSESSMENT_STORE_API_HOST = CommonConfig.ASSESSMENT_STORE_API_HOST
    ACCOUNT_STORE_API_HOST = CommonConfig.ACCOUNT_STORE_API_HOST

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

    # Assessment store endpoints
    APPLICATION_OVERVIEW_ENDPOINT_FUND_ROUND_PARAMS = (
        "/application_overviews/{fund_id}/{round_id}?{params}"
    )

    APPLICATION_OVERVIEW_ENDPOINT_APPLICATION_ID = (
        "/application_overviews/{application_id}"
    )

    SUB_CRITERIA_THEME_ANSWERS_ENDPOINT = (
        "/sub_criteria_themes/{application_id}/{theme_id}"
    )

    SUB_CRITERIA_OVERVIEW_ENDPOINT = (
        "/sub_criteria_overview/{application_id}/{sub_criteria_id}"
    )

    BANNER_STATE_ENDPOINT = (
        "/sub_criteria_overview/banner_state/{application_id}"
    )

    ASSESSMENT_SCORES_ENDPOINT = ASSESSMENT_STORE_API_HOST + "/score"

    ASSESSMENT_COMMENT_ENDPOINT = ASSESSMENT_STORE_API_HOST + "/comment"

    ASSESSMENT_FLAGS_ENDPOINT = ASSESSMENT_STORE_API_HOST + "/flag"

    COMMENTS_ENDPOINT = (
        "/comment/{application_id}/{sub_criteria_id}/{theme_id}"
    )

    # Account store endoints
    BULK_ACCOUNTS_ENDPOINT = ACCOUNT_STORE_API_HOST + "/bulk-accounts"

    """
    Assets
    """
    ASSETS_DEBUG = False
    ASSETS_AUTO_BUILD = True

    TALISMAN_SETTINGS = CommonConfig.TALISMAN_SETTINGS

    COF_FUND_ID = CommonConfig.COF_FUND_ID
    COF_ROUND2_ID = CommonConfig.COF_ROUND_2_ID

    USE_LOCAL_DATA = strtobool(getenv("USE_LOCAL_DATA", "False"))

    """
    Aws Config
    """

    AWS_ACCESS_KEY_ID = getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = getenv("AWS_SECRET_ACCESS_KEY")
    AWS_BUCKET_NAME = getenv("AWS_BUCKET_NAME")
    AWS_REGION = "eu-west-2"
