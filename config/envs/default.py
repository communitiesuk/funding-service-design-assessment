import base64
import os
from os import environ
from os import getenv
from pathlib import Path

from distutils.util import strtobool
from fsd_utils import CommonConfig
from fsd_utils import configclass
from fsd_utils.toggles.vcap_services import VcapServices


@configclass
class DefaultConfig:

    # ---------------
    #  General App Config
    # ---------------

    SECRET_KEY = CommonConfig.SECRET_KEY
    SESSION_COOKIE_NAME = CommonConfig.SESSION_COOKIE_NAME
    FLASK_ROOT = str(Path(__file__).parent.parent.parent)
    FLASK_ENV = CommonConfig.FLASK_ENV
    TEXT_AREA_INPUT_MAX_CHARACTERS = 10000

    # Authentication
    FSD_USER_TOKEN_COOKIE_NAME = "fsd_user_token"
    AUTHENTICATOR_HOST = environ.get("AUTHENTICATOR_HOST", "authenticator")
    # RSA 256 KEYS
    RSA256_PUBLIC_KEY_BASE64 = environ.get("RSA256_PUBLIC_KEY_BASE64")
    if RSA256_PUBLIC_KEY_BASE64:
        RSA256_PUBLIC_KEY = base64.b64decode(RSA256_PUBLIC_KEY_BASE64).decode()

    FORCE_HTTPS = CommonConfig.FORCE_HTTPS
    FSD_LOG_LEVEL = CommonConfig.FSD_LOG_LEVEL
    FSD_USER_TOKEN_COOKIE_NAME = "fsd_user_token"

    STATIC_FOLDER = "app/static/dist"
    STATIC_URL_PATH = "app/static"
    TEMPLATES_FOLDER = "templates"
    LOCAL_SERVICE_NAME = "local_flask"
    ASSESSMENT_HUB_ROUTE = "/assess"
    DASHBOARD_ROUTE = "/assess/assessor_tool_dashboard"

    # Assessement settings
    SHOW_ALL_ROUNDS = strtobool(getenv("SHOW_ALL_ROUNDS", "False"))

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
    FUND_ENDPOINT = (
        CommonConfig.FUND_ENDPOINT + "?use_short_name={use_short_name}"
    )
    GET_ROUND_DATA_FOR_FUND_ENDPOINT = (
        FUND_STORE_API_HOST + "/funds/{fund_id}/rounds/{round_id}"
    )
    # TODO: Rework on the avialable teams allocated after implemented in fundstore
    GET_AVIALABLE_TEAMS_FOR_FUND = (
        FUND_STORE_API_HOST
        + "/funds/{fund_id}/rounds/{round_id}/available_flag_allocations"
    )

    # Round Store Endpoints

    ROUNDS_ENDPOINT = CommonConfig.ROUNDS_ENDPOINT
    ROUND_ENDPOINT = (
        CommonConfig.ROUND_ENDPOINT + "?use_short_name={use_short_name}"
    )

    # Application Store Endpoints
    APPLICATION_ENDPOINT = CommonConfig.APPLICATION_ENDPOINT
    APPLICATION_STATUS_ENDPOINT = CommonConfig.APPLICATION_STATUS_ENDPOINT
    APPLICATION_SEARCH_ENDPOINT = CommonConfig.APPLICATION_SEARCH_ENDPOINT

    # Assessment store endpoints
    ASSESSMENTS_STATS_ENDPOINT = (
        "/assessments/get-stats/{fund_id}/{round_id}?{params}"
    )
    APPLICATION_OVERVIEW_ENDPOINT_FUND_ROUND_PARAMS = (
        "/application_overviews/{fund_id}/{round_id}?{params}"
    )
    APPLICATION_OVERVIEW_FLAGS_V2_ENDPOINT_FUND_ROUND_PARAMS = (
        "/application_overviews_flags_v2/{fund_id}/{round_id}?{params}"
    )

    APPLICATION_OVERVIEW_ENDPOINT_APPLICATION_ID = (
        "/application_overviews/{application_id}"
    )

    APPLICATION_JSON_ENDPOINT = (
        ASSESSMENT_STORE_API_HOST + "/application/{application_id}/json"
    )

    APPLICATION_JSON_ENDPOINT = (
        ASSESSMENT_STORE_API_HOST + "/application/{application_id}/json"
    )

    APPLICATION_METADATA_ENDPOINT = (
        ASSESSMENT_STORE_API_HOST + "/application/{application_id}/metadata"
    )

    SUB_CRITERIA_THEME_ANSWERS_ENDPOINT = (
        "/sub_criteria_themes/{application_id}/{theme_id}"
    )

    SUB_CRITERIA_OVERVIEW_ENDPOINT = (
        "/sub_criteria_overview/{application_id}/{sub_criteria_id}"
    )

    SUB_CRITERIA_BANNER_STATE_ENDPOINT = (
        "/sub_criteria_overview/banner_state/{application_id}"
    )

    ASSESSMENT_SCORES_ENDPOINT = ASSESSMENT_STORE_API_HOST + "/score"
    ASSESSMENT_UPDATE_STATUS = (
        ASSESSMENT_STORE_API_HOST
        + "/application/{application_id}/status/complete"
    )
    ASSESSMENT_UPDATE_QA_STATUS = (
        ASSESSMENT_STORE_API_HOST
        + "/application/{application_id}/status/qa_complete"
    )

    ASSESSMENT_COMMENT_ENDPOINT = ASSESSMENT_STORE_API_HOST + "/comment"
    ASSESSMENT_PROGRESS_ENDPOINT = ASSESSMENT_STORE_API_HOST + "/progress"

    ASSESSMENT_LATEST_FLAG_ENDPOINT = (
        ASSESSMENT_STORE_API_HOST + "/flag?application_id={application_id}"
    )

    ASSESSMENT_FLAG_ENDPOINT = (
        ASSESSMENT_STORE_API_HOST + "/flag_data?flag_id={flag_id}"
    )
    ASSESSMENT_FLAGS_ENDPOINT = (
        ASSESSMENT_STORE_API_HOST + "/flags?application_id={application_id}"
    )

    # TODO : Need to rework on this once old rounds are migrated to use new flags
    ASSESSMENT_FLAGS_V2_ENDPOINT = (
        ASSESSMENT_STORE_API_HOST + "/flags_v2/{application_id}"
    )
    ASSESSMENT_FLAGS_V2_POST_ENDPOINT = (
        ASSESSMENT_STORE_API_HOST + "/flags_v2/"
    )
    ASSESSMENT_FLAG_V2_ENDPOINT = (
        ASSESSMENT_STORE_API_HOST + "/flag_data_v2?flag_id={flag_id}"
    )
    ASSESSMENT_AVAILABLE_TAGS_ENDPOINT = (
        ASSESSMENT_STORE_API_HOST + "/funds/{fund_id}/rounds/{round_id}/tags"
    )

    # Account store endpoints
    BULK_ACCOUNTS_ENDPOINT = ACCOUNT_STORE_API_HOST + "/bulk-accounts"

    """
    Assets
    """
    ASSETS_DEBUG = False
    ASSETS_AUTO_BUILD = True

    TALISMAN_SETTINGS = CommonConfig.TALISMAN_SETTINGS

    COF_FUND_ID = "47aef2f5-3fcb-4d45-acb5-f0152b5f03c4"
    COF_ROUND_2_ID = "c603d114-5364-4474-a0c4-c41cbf4d3bbd"
    COF_ROUND_2_W3_ID = "5cf439bf-ef6f-431e-92c5-a1d90a4dd32f"

    DEFAULT_FUND_ID = COF_FUND_ID
    DEFAULT_ROUND_ID = COF_ROUND_2_W3_ID

    """
    Aws Config
    """

    if "VCAP_SERVICES" in os.environ:
        VCAP_SERVICES = VcapServices.from_env_json(
            environ.get("VCAP_SERVICES")
        )

        if VCAP_SERVICES.does_service_exist(service_key="aws-s3-bucket"):
            s3_credentials = VCAP_SERVICES.get_service_credentials_value(
                "aws-s3-bucket"
            )
            AWS_REGION = s3_credentials["aws_region"]
            AWS_ACCESS_KEY_ID = s3_credentials["aws_access_key_id"]
            AWS_SECRET_ACCESS_KEY = s3_credentials["aws_secret_access_key"]
            AWS_BUCKET_NAME = s3_credentials["bucket_name"]

    # Redis Feature Toggle Configuration
    REDIS_INSTANCE_URI = getenv("REDIS_INSTANCE_URI", "redis://localhost:6379")
    TOGGLES_URL = REDIS_INSTANCE_URI + "/0"
    FEATURE_CONFIG = {"TAGGING": False}
