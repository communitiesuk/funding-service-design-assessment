from config.envs.default import DefaultConfig
from fsd_utils import configclass


@configclass
class DevConfig(DefaultConfig):
    # Redis Feature Toggle Configuration
    REDIS_INSTANCE_NAME = "funding-service-magic-links-dev"
    REDIS_INSTANCE_URI = (
        DefaultConfig.VCAP_SERVICES.get_service_credentials_value(
            "redis", REDIS_INSTANCE_NAME, "uri"
        )
    )
    TOGGLES_URL = REDIS_INSTANCE_URI + "/0"

    FSD_LOG_LEVEL = "DEBUG"
