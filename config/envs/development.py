import logging

from config.envs.default import DefaultConfig
from fsd_utils import configclass


@configclass
class DevelopmentConfig(DefaultConfig):

    FSD_LOG_LEVEL = logging.INFO

    FUND_STORE_API_HOST = "http://fund-store:8080"
    ASSESSMENT_STORE_API_HOST = "http://assessment-store:8080"
    APPLICATION_STORE_API_HOST = "http://application-store:8080"

    # for local dev/test use with flask run and USE_LOCAL_DATA = False:
    USE_LOCAL_DATA = False
    ASSESSMENT_SCORES_ENDPOINT = ASSESSMENT_STORE_API_HOST + "/score"