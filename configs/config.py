from dataclasses import dataclass

from omegaconf import OmegaConf, DictConfig

from helpers import get_path

CONFIG_PATH = get_path('config.yaml')


@dataclass
class Config:
    vk_api: DictConfig
    parsing: 'Parsing'
    progressbar: 'Progressbar'
    display_types: 'DisplayTypes'
    paths: 'Paths'
    exceptions: DictConfig

    def __init__(self):
        data = OmegaConf.load(CONFIG_PATH)
        self.vk_api = data.vk_api
        self.parsing = self.Parsing(data.get('parsing'))
        self.progressbar = self.Progressbar(data.get('progressbar'))
        self.display_types = self.DisplayTypes(data.get('display_types'))
        self.paths = self.Paths(data.get('paths'))
        self.exceptions = data.get('exceptions')

    @dataclass
    class Parsing:
        max_links_per_widget: int
        skip_correct: bool
        save_public_data: bool
        public_data_fields: list

        def __init__(self, data: DictConfig = None):
            if not data:
                data = {}

            self.max_links_per_widget = data.get('max_links_per_widget', 0)
            self.skip_correct = data.get('skip_correct', False)
            self.save_public_data = data.get('save_public_data', True)
            self.public_data_fields = data.get('fields', ['menu'])

    @dataclass
    class Progressbar:
        min_interval_per_unit: float

        def __init__(self, data: DictConfig):
            if not data:
                data = {}

            self.min_interval_per_unit = data.get('min_interval_per_unit', 0.)

    @dataclass
    class DisplayTypes:
        csv_delimiter: str
        status_types: 'Type'
        result_types: 'Type'

        @dataclass
        class Type:
            pattern: str
            items: dict

            def __init__(self, pattern: str, items: dict):
                self.pattern = pattern
                self.items = items

        def __init__(self, data: DictConfig):
            if not data:
                data = {}

            self.csv_delimiter = data.get('csv_delimiter', ';')
            self.status_types = self.Type(**data.get('status_types', dict(
                pattern='{name}: {value}',
                items=dict(
                    VALID=dict(name='Correct', value=''),
                    NOT_MATCH=dict(name='Invalid, url don\'t match pattern', value=''),
                    UTM_INVALID=dict(name='Invalid UTM code value', value=''),
                    SPACER=dict(name='Invalid, url contains spaces', value='')
                )
            )))
            self.result_types = self.Type(**data.get('result_types', dict(
                pattern='{name}',
                items=dict(
                    CORRECT=dict(name='Widgets exists and urls is correct', value=''),
                    INVALID=dict(name='Widgets exists and urls NOT valid', value=''),
                    LINKS_COUNT=dict(name='Widgets exists and urls count NOT correct', value=''),
                    MISSING=dict(name='Widgets NOT exists', value=''),
                    TIMEOUT=dict(name='Can\'t get url page data', value=''),
                    ERROR=dict(name='NOT valid url or parsing errors', value='')
                )
            )))

    @dataclass
    class Paths:
        log_file: str
        target_file: str
        result_file: str
        save_public_data_dir: str

        def __init__(self, data: DictConfig):
            if not data:
                data = {}

            self.log_file = get_path(data.get('log_file', 'runtime.log'))
            self.target_file = get_path(data.get('target_file', 'target.txt'))
            self.result_file = get_path(data.get('result_file', 'result.csv'))
            self.save_public_data_dir = get_path(data.get('save_public_data_dir', 'publics_data'))


CONFIG = Config()
