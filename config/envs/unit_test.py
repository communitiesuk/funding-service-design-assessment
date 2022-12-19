from config.envs.default import DefaultConfig
from fsd_utils import configclass
from os import getenv


@configclass
class UnitTestConfig(DefaultConfig):
    DefaultConfig.TALISMAN_SETTINGS["force_https"] = False
    USE_LOCAL_DATA = True

    AWS_ACCESS_KEY_ID =" CommonConfig.AWS_ACCESS_KEY_ID"

    """
    Aws Config
    """

    AWS_ACCESS_KEY_ID = getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY =  getenv("AWS_SECRET_ACCESS_KEY")
    AWS_BUCKET_NAME = getenv("AWS_BUCKET_NAME")
    AWS_REGION = getenv("AWS_REGION")
