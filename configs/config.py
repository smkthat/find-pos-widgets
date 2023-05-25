from dataclasses import dataclass

from omegaconf import OmegaConf, DictConfig

from helpers import get_path

CONFIG_PATH = get_path('config.yaml')


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
TARGET_FILE_PATH = get_path(CONFIG.log.get('target_file_path', 'target.txt'))
RESULT_FILE_PATH = get_path(CONFIG.log.get('result_file_path', 'result.csv'))
LOG_FILE_PATH = get_path(CONFIG.log.get('log_file_path', 'runtime.log'))
SAVE_PUBLIC_DATA_DIR = get_path(CONFIG.parsing.get('save_public_data_dir', None))
