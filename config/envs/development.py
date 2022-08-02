import logging
from os import getenv

from config.envs.default import DefaultConfig
from fsd_utils import configclass
from distutils.util import strtobool


@configclass
class DevelopmentConfig(DefaultConfig):
    FSD_LOG_LEVEL = logging.DEBUG
    ASSESSMENT_STORE_API_HOST = "https://funding-service-design-assessment-store-dev.london.cloudapps.digital"
    ASSESSMENT_SCORE_JUST_ENDPOINT = ASSESSMENT_STORE_API_HOST+"/assessments/{assessment_id}/sub_criterias/{sub_criteria_id}/scores"
    USE_LOCAL_DATA = strtobool(getenv("USE_LOCAL_DATA", "True"))