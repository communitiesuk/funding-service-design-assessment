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

    ASSESSMENT_SCORES_ENDPOINT = (
        ASSESSMENT_STORE_API_HOST
        + "/assessments/{assessment_id}/sub_criterias/{sub_criteria_id}/scores"
    )

    """
    Assets
    """
    ASSETS_DEBUG = False
    ASSETS_AUTO_BUILD = True

    # TODO reinstate secure settings
    # TALISMAN_SETTINGS = CommonConfig.TALISMAN_SETTINGS
    # Content Security Policy
    SECURE_CSP = {
        "default-src": "'self'",
        "script-src": [
            "'self'",
            # "'sha256-+6WnXIl4mbFTCARd8N3COQmT3bJJmo32N8q8ZSQAIcU='",
            # "'sha256-l1eTVSK8DTnK8+yloud7wZUqFrI0atVo6VlC6PJvYaQ='",
            # "'sha256-bhyBXL9pVXmONqYU0zC4tGLHyo1DT/oTdferhgC1Gtk='",
            # "'sha256-mWb4da+NTy9q386BUtnJIL4Z9Z4vQWJVGOof4mBCvMw='",
            "'unsafe-inline'",
        ],
        "connect-src": "",  # APPLICATION_STORE_API_HOST_PUBLIC,
        "img-src": ["data:", "'self'"],
    }
    TALISMAN_SETTINGS = {
        "feature_policy": CommonConfig.FSD_FEATURE_POLICY,
        "permissions_policy": CommonConfig.FSD_PERMISSIONS_POLICY,
        "document_policy": CommonConfig.FSD_DOCUMENT_POLICY,
        "force_https": FORCE_HTTPS,
        "force_https_permanent": False,
        "force_file_save": False,
        "frame_options": "SAMEORIGIN",
        "frame_options_allow_from": None,
        "strict_transport_security": True,
        "strict_transport_security_preload": True,
        "strict_transport_security_max_age": CommonConfig.ONE_YEAR_IN_SECS,
        "strict_transport_security_include_subdomains": True,
        "content_security_policy": SECURE_CSP,
        "content_security_policy_report_uri": None,
        "content_security_policy_report_only": False,
        "content_security_policy_nonce_in": None,
        "referrer_policy": CommonConfig.FSD_REFERRER_POLICY,
        "session_cookie_secure": True,
        "session_cookie_http_only": True,
        "session_cookie_samesite": CommonConfig.FSD_SESSION_COOKIE_SAMESITE,
        "x_content_type_options": True,
        "x_xss_protection": True,
    }

    COF_FUND_ID = CommonConfig.COF_FUND_ID
    COF_ROUND2_ID = CommonConfig.COF_ROUND_2_ID

    USE_LOCAL_DATA = strtobool(getenv("USE_LOCAL_DATA", "False"))
