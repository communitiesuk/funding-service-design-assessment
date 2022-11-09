from config.envs.default import DefaultConfig
from fsd_utils import configclass


@configclass
class DevelopmentConfig(DefaultConfig):
    ASSESSMENT_SCORE_JUST_ENDPOINT = (
        DefaultConfig.ASSESSMENT_STORE_API_HOST
        + "/assessments/{assessment_id}/sub_criterias/{sub_criteria_id}/scores"
    )
    USE_LOCAL_DATA = True
