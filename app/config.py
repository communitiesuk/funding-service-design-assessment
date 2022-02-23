"""Flask configuration."""
from os import environ
from os import path

"""
Application Config
"""
SECRET_KEY = environ.get("SECRET_KEY") or "dev"
SESSION_COOKIE_NAME = environ.get("SESSION_COOKIE_NAME") or "session_cookie"
STATIC_FOLDER = "static"
TEMPLATES_FOLDER = "templates"
LOCAL_SERVICE_NAME = "local_flask"
ASSESSMENT_HUB_ROUTE = "/assess"
FLASK_ROOT = path.dirname(path.dirname(path.realpath(__file__)))
FLASK_ENV = environ.get("FLASK_ENV")
TESTING = FLASK_ENV == "test" or False

"""
APIs Config
"""
TEST_FUND_STORE_API_HOST = "sample_api_data/fund_store"
TEST_APPLICATION_STORE_API_HOST = "sample_api_data/application_store"

FUND_STORE_API_HOST = environ.get("FUND_STORE_API_HOST") or TEST_FUND_STORE_API_HOST
APPLICATION_STORE_API_HOST = (
    environ.get("APPLICATION_STORE_API_HOST") or TEST_APPLICATION_STORE_API_HOST
)
