import logging

from config.envs.default import DefaultConfig
from fsd_utils import configclass


@configclass
class DevelopmentConfig(DefaultConfig):
    FSD_LOG_LEVEL = logging.DEBUG
    ASSESSMENT_STORE_API_HOST = "https://funding-service-design-assessment-store-dev.london.cloudapps.digital"
