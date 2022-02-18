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
APPLICATION_ROOT = path.dirname(path.dirname(path.realpath(__file__)))

"""
APIs Config
"""
FUND_STORE_API_ROOT = environ.get("FUND_STORE_API_ROOT") or "sample_api_data/fund_store/"
APPLICATION_STORE_API_ROOT = (
    environ.get("APPLICATION_STORE_API_ROOT") or "sample_api_data/application_store/"
)
