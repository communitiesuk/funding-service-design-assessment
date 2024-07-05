from fsd_utils import configclass

from config.envs.default import DefaultConfig


@configclass
class DevConfig(DefaultConfig):
    # Redis Feature Toggle Configuration
    REDIS_INSTANCE_NAME = "funding-service-magic-links-dev"
    FSD_LOG_LEVEL = "DEBUG"
