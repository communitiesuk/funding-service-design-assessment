from config.envs.default import DefaultConfig
from fsd_utils import CommonConfig
from fsd_utils import configclass


@configclass
class ProductionConfig(DefaultConfig):
    """
    Feature Toggles
    """

    FEATURE_CONFIG = CommonConfig.prod_feature_configuration
