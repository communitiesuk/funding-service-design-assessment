from config.envs.default import DefaultConfig
from fsd_utils import configclass
from os import getenv


@configclass
class UnitTestConfig(DefaultConfig):
    DefaultConfig.TALISMAN_SETTINGS["force_https"] = False
    USE_LOCAL_DATA = True