import os
from dataclasses import dataclass

from omegaconf import OmegaConf, DictConfig

CONFIG_PATH = os.path.abspath(os.path.join(os.getcwd(), os.path.join('..', 'config.yaml')))


@dataclass
class Config:
    vk_api: DictConfig
    parsing: DictConfig
    log: DictConfig
    exceptions: DictConfig

    def __init__(self):
        data = OmegaConf.load(CONFIG_PATH)
        self.vk_api = data.vk_api
        self.parsing = data.parsing
        self.log = data.log
        self.exceptions = data.exceptions


CONFIG = Config()
