from dataclasses import dataclass

from omegaconf import OmegaConf, DictConfig

from helpers import get_path

CONFIG_PATH = get_path('config.yaml')


@dataclass
class Config:
    vk_api: DictConfig
    parsing: 'Parsing'
    log: DictConfig
    exceptions: DictConfig

    def __init__(self):
        data = OmegaConf.load(CONFIG_PATH)
        self.vk_api = data.vk_api
        self.parsing = self.Parsing(data.parsing)
        self.log = data.log
        self.exceptions = data.exceptions

    @dataclass
    class Parsing:
        min_interval: float
        status: DictConfig
        result: DictConfig
        skip_correct: bool
        save_public_data_dir: str
        fields: list

        def __init__(self, data: DictConfig = None):
            if not data:
                data = {}

            self.min_interval = data.get('min_interval', 0.)
            self.status = data.get('status', dict(
                VALID='Correct',
                NOT_MATCH='Invalid, url don\'t match pattern',
                UTM_INVALID='Invalid UTM code value',
                SPACER='Invalid, url contains spaces'
            ))
            self.result = data.get('result', dict(
                CORRECT='Widgets exists and urls is correct',
                INVALID='Widgets exists and urls NOT valid',
                MISSING='Widgets NOT exists',
                TIMEOUT='Can\'t get url page data',
                ERROR='NOT valid url or parsing errors',
            ))
            self.skip_correct = data.get('skip_correct', False)
            self.save_public_data_dir = data.get('save_public_data_dir', 'publics_data')
            self.fields = data.get('fields', ['menu'])


CONFIG = Config()
TARGET_FILE_PATH = get_path(CONFIG.log.get('target_file_path', 'target.txt'))
RESULT_FILE_PATH = get_path(CONFIG.log.get('result_file_path', 'result.csv'))
LOG_FILE_PATH = get_path(CONFIG.log.get('log_file_path', 'runtime.log'))
SAVE_PUBLIC_DATA_DIR = get_path(CONFIG.parsing.save_public_data_dir)
