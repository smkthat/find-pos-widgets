from dataclasses import dataclass
from typing import List, Dict

from omegaconf import OmegaConf, DictConfig

from helpers import get_path

CONFIG_PATH = get_path('config.yaml')


@dataclass
class Config:
    _vk_api: DictConfig
    _parsing: 'Parsing'
    _progressbar: 'Progressbar'
    _display: 'Display'
    _paths: 'Paths'
    _exceptions: DictConfig

    @property
    def vk_api(self) -> DictConfig:
        return self._vk_api

    @property
    def parsing(self) -> 'Parsing':
        return self._parsing

    @property
    def progressbar(self) -> 'Progressbar':
        return self._progressbar

    @property
    def display(self) -> 'Display':
        return self._display

    @property
    def paths(self) -> 'Paths':
        return self._paths

    @property
    def exceptions(self) -> 'Exceptions':
        return self._exceptions

    def __init__(self, data: DictConfig) -> None:
        self._vk_api = data.vk_api
        self._parsing = self.Parsing(data.get('parsing'))
        self._progressbar = self.Progressbar(data.get('progressbar'))
        self._display = self.Display(data.get('display'))
        self._paths = self.Paths(data.get('paths'))
        self._exceptions = self.Exceptions(data.get('exceptions'))

    @dataclass
    class Parsing:
        _max_links_per_widget: int
        _skip_correct: bool
        _save_public_data: bool
        _public_data_fields: list

        @property
        def max_links_per_widget(self) -> int:
            return self._max_links_per_widget

        @property
        def skip_correct(self) -> bool:
            return self._skip_correct

        @property
        def save_public_data(self) -> bool:
            return self._save_public_data

        @property
        def public_data_fields(self) -> List[str]:
            return self._public_data_fields

        def __init__(self, data: DictConfig = None) -> None:
            if not data:
                data = {}

            self._max_links_per_widget = data.get('max_links_per_widget', 0)
            self._skip_correct = data.get('skip_correct', False)
            self._save_public_data = data.get('save_public_data', True)
            self._public_data_fields = data.get('fields', ['menu'])

    @dataclass
    class Progressbar:
        min_interval_per_unit: float

        def __init__(self, data: DictConfig) -> None:
            if not data:
                data = {}

            self.min_interval_per_unit = data.get('min_interval_per_unit', 0.)

    @dataclass
    class Display:
        _csv_delimiter: str
        _public_display_fields: list
        _show_utm_status: bool
        _codes_hints: 'Type'
        _status_types: 'Type'
        _result_types: 'Type'

        @property
        def csv_delimiter(self) -> str:
            return self._csv_delimiter

        @property
        def public_display_fields(self) -> List[str]:
            return self._public_display_fields

        @property
        def show_utm_status(self) -> bool:
            return self._show_utm_status

        @property
        def codes_hints(self) -> 'Type':
            return self._codes_hints

        @property
        def status_types(self) -> 'Type':
            return self._status_types

        @property
        def result_types(self) -> 'Type':
            return self._result_types

        @dataclass
        class Type:
            _pattern: str
            _items: dict

            @property
            def pattern(self) -> str:
                return self._pattern

            @property
            def items(self) -> Dict:
                return self._items

            def __init__(self, pattern: str, items: dict):
                self._pattern = pattern
                self._items = items

        def __init__(self, data: DictConfig) -> None:
            if not data:
                data = {}

            self._csv_delimiter = data.get('csv_delimiter', ';')
            self._public_display_fields = data.get('public_display_fields', [
                'pos_result', 'url', 'name', 'pos_links'
            ])
            self._show_utm_status = data.get('show_utm_status', True)
            self._codes_hints = self.Type(**data.get('codes_hints', dict(
                pattern='{param}={value} ({code}: {hint})',
                items=dict(
                    ID='Only digits expected',
                    REG_CODE='Only 2 digits expected or one from this values: 111, 711, 7114',
                    MIN_CODE='Only 8 digits expected',
                    OGRN='Only 13 digits',
                    SOURCE='Only one from this values expected: vk, vk1, vk2',
                    UNDEFINED='Undefined UTM-code'
                )
            )))
            self._status_types = self.Type(**data.get('status_types', dict(
                pattern='{name}: {value}',
                items=dict(
                    VALID=dict(name='Correct', value=''),
                    NOT_MATCH=dict(name='Invalid, url don\'t match pattern', value=''),
                    UTM_INVALID=dict(name='Invalid UTM code value', value=''),
                    SPACER=dict(name='Invalid, url contains spaces', value='')
                )
            )))
            self._result_types = self.Type(**data.get('result_types', dict(
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
        _log_file: str
        _target_file: str
        _result_file: str
        _save_public_data_dir: str

        @property
        def log_file(self) -> str:
            return self._log_file

        @property
        def target_file(self) -> str:
            return self._target_file

        @property
        def result_file(self) -> str:
            return self._result_file

        @property
        def save_public_data_dir(self) -> str:
            return self._save_public_data_dir

        def __init__(self, data: DictConfig) -> None:
            if not data:
                data = {}

            self._log_file = get_path(data.get('log_file', 'runtime.log'))
            self._target_file = get_path(data.get('target_file', 'target.txt'))
            self._result_file = get_path(data.get('result_file', 'result.csv'))
            self._save_public_data_dir = get_path(data.get('save_public_data_dir', 'publics_data'))

    @dataclass
    class Exceptions:
        _connection: Dict

        @property
        def connection(self) -> Dict:
            return self._connection

        def __init__(self, data: DictConfig) -> None:
            if not data:
                data = {}

            self._connection = data.get('connection', dict(
                max_tries=5,
                timeout=5
            ))


CONFIG = Config(data=OmegaConf.load(CONFIG_PATH))
