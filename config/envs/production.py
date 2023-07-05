from config.envs.default import DefaultConfig
from fsd_utils import configclass


@configclass
class ProductionConfig(DefaultConfig):
    # Redis Feature Toggle Configuration
    REDIS_INSTANCE_NAME = "funding-service-magic-links"
    REDIS_INSTANCE_URI = (
        DefaultConfig.vcap_services.get_service_credentials_value(
            "redis", REDIS_INSTANCE_NAME, "uri"
        )
    )
    TOGGLES_URL = REDIS_INSTANCE_URI + "/0"
