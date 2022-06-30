import os
from pathlib import Path

from fsd_utils import configclass


@configclass
class DefaultConfig:
    """
    Application Config
    """

    print("loading default config ")
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

    print(
        "APPLICATION_STORE_API_HOST_PUBLIC", APPLICATION_STORE_API_HOST_PUBLIC
    )
