from config.envs.default import DefaultConfig
from fsd_utils import configclass


@configclass
class DevelopmentConfig(DefaultConfig):
    ASSESSMENT_SCORES_ENDPOINT = (
        DefaultConfig.ASSESSMENT_STORE_API_HOST
        + "/assessments/{assessment_id}/sub_criterias/{sub_criteria_id}/scores"
    )

    USE_LOCAL_DATA = True
    # USE_LOCAL_DATA = False

    # FUND_STORE_API_HOST =
    # "https://funding-service-design-fund-store-dev.london.cloudapps.digital"
    # ASSESSMENT_STORE_API_HOST =
    # "https://funding-service-design-assessment-store-dev.london.cloudapps.digital"
