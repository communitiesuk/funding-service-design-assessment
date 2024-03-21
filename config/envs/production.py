from fsd_utils import configclass

from config.envs.default import DefaultConfig


@configclass
class ProductionConfig(DefaultConfig):
    # Redis Feature Toggle Configuration
    REDIS_INSTANCE_NAME = "funding-service-magic-links"

    if not hasattr(DefaultConfig, "VCAP_SERVICES"):
        REDIS_INSTANCE_URI = DefaultConfig.REDIS_INSTANCE_URI
    else:
        REDIS_INSTANCE_URI = DefaultConfig.VCAP_SERVICES.get_service_credentials_value(
            "redis", REDIS_INSTANCE_NAME, "uri"
        )

    TOGGLES_URL = REDIS_INSTANCE_URI + "/0"
