import os
from pathlib import Path

from fsd_utils import configclass


@configclass
class DefaultConfig:
    """
    Application Config
    """

    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev"
    SESSION_COOKIE_NAME = (
        os.environ.get("SESSION_COOKIE_NAME") or "session_cookie"
    )
    STATIC_FOLDER = "static"
    TEMPLATES_FOLDER = "templates"
    LOCAL_SERVICE_NAME = "local_flask"
    ASSESSMENT_HUB_ROUTE = "/assess"
    FLASK_ROOT = str(Path(__file__).parent.parent.parent)
    FLASK_ENV = os.environ.get("FLASK_ENV") or "development"

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

    FUND_STORE_API_HOST = (
        os.environ.get("FUND_STORE_API_HOST") or TEST_FUND_STORE_API_HOST
    )
    ROUND_STORE_API_HOST = (
        os.environ.get("ROUND_STORE_API_HOST") or TEST_ROUND_STORE_API_HOST
    )
    APPLICATION_STORE_API_HOST = (
        os.environ.get("APPLICATION_STORE_API_HOST")
        or TEST_APPLICATION_STORE_API_HOST
    )

    APPLICATION_STORE_API_HOST_PUBLIC = (
        os.environ.get("APPLICATION_STORE_API_HOST_PUBLIC")
        or os.environ.get("APPLICATION_STORE_API_HOST")
        or "/api/" + TEST_APPLICATION_STORE_API_HOST
    )

    """Content Security Policy"""
    SECURE_CSP = {
        "default-src": "'self'",
        "script-src": [
            "'self'",
            "'sha256-+6WnXIl4mbFTCARd8N3COQmT3bJJmo32N8q8ZSQAIcU='",
            "'sha256-l1eTVSK8DTnK8+yloud7wZUqFrI0atVo6VlC6PJvYaQ='",
        ],
        "connect-src": "",  # APPLICATION_STORE_API_HOST_PUBLIC,
        "img-src": ["data:", "'self'"],
    }

    """Talisman Config"""

    # Security headers and other policies
    FSD_REFERRER_POLICY = "strict-origin-when-cross-origin"
    FSD_SESSION_COOKIE_SAMESITE = "Lax"
    FSD_PERMISSIONS_POLICY = {"interest-cohort": "()"}
    FSD_DOCUMENT_POLICY = {}
    FSD_FEATURE_POLICY = {
        "microphone": "'none'",
        "camera": "'none'",
        "geolocation": "'none'",
    }

    DENY = "DENY"
    SAMEORIGIN = "SAMEORIGIN"
    ALLOW_FROM = "ALLOW-FROM"
    ONE_YEAR_IN_SECS = 31556926

    FORCE_HTTPS = True

    TALISMAN_SETTINGS = {
        "feature_policy": FSD_FEATURE_POLICY,
        "permissions_policy": FSD_PERMISSIONS_POLICY,
        "document_policy": FSD_DOCUMENT_POLICY,
        "force_https": FORCE_HTTPS,
        "force_https_permanent": False,
        "force_file_save": False,
        "frame_options": "SAMEORIGIN",
        "frame_options_allow_from": None,
        "strict_transport_security": True,
        "strict_transport_security_preload": True,
        "strict_transport_security_max_age": ONE_YEAR_IN_SECS,
        "strict_transport_security_include_subdomains": True,
        "content_security_policy": SECURE_CSP,
        "content_security_policy_report_uri": None,
        "content_security_policy_report_only": False,
        "content_security_policy_nonce_in": None,
        "referrer_policy": FSD_REFERRER_POLICY,
        "session_cookie_secure": True,
        "session_cookie_http_only": True,
        "session_cookie_samesite": FSD_SESSION_COOKIE_SAMESITE,
        "x_content_type_options": True,
        "x_xss_protection": True,
    }
