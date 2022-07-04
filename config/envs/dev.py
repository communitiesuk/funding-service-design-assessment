import logging

from config.envs.default import DefaultConfig
from fsd_utils import configclass


@configclass
class Dev(DefaultConfig):
    FSD_LOG_LEVEL = logging.INFO
