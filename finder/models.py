import re
import enum
from typing import List, Dict, Tuple, Union
from urllib.parse import urlparse, parse_qs

from configs import get_logger, CONFIG

logger = get_logger(__name__)


class Public:
    __url: str
    is_government_org: Union[bool, None] = None
    pos_widget: 'PosWidget'
    data: dict

    def __init__(self, url: str):
        self.__url = url
        self.pos_widget = PosWidget()
        self.data = {}

    @property
    def url(self):
        return self.__url

    @property
    def identify(self) -> str:
        split_url = self.__url.split('/')
        return split_url[-1] if split_url else ''

    def get_field_data(self, field: str):
        field_attrs = field.split('.')
        field_name = field_attrs.pop(0)
        field_data = self.data.get(field_name, '')
        if field_attrs:
            for attr in field_attrs:
                if isinstance(field_data, dict):
                    field_data = field_data.get(attr, '')
        return field_data

    def parse(self, data: dict) -> 'Public':
        if not data:
            self.pos_widget.result = PosWidget.ResultType.ERROR
            return self
        self.is_government_org = data.get('is_government_org', None)
        self.pos_widget.parse_data(data)
        self.data = data
        return self


class UTMCode:
    _code: str
    _param: str = None
    _pattern: str = None
    _value: str = None
    _hint: str = 'Undefined UTM-code'
    _is_valid: bool = False

    def __init__(self, code: str = None, hint: str = None, pattern: str = None) -> None:
        if code:
            self._code = code
        if hint:
            self._hint = hint
        if pattern:
            self._pattern = pattern

    @property
    def param(self) -> str:
        return self._param

    @param.setter
    def param(self, param: str) -> None:
        self._param = param

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value: str) -> None:
        self._value = value
        self.validate()

    @property
    def hint(self) -> str:
        return self._hint

    @property
    def is_valid(self) -> bool:
        return self._is_valid

    def validate(self) -> None:
        if self._pattern:
            pattern = re.compile(self._pattern)
            match = re.fullmatch(pattern, self._value)
            self._is_valid = bool(match)

    def __str__(self):
        codes_hints = CONFIG.display.codes_hints
        hint = codes_hints.items.get(self._code)
        return codes_hints.pattern.format(
            code=self._code,
            param=self._param,
            pattern=f'{self._pattern!r}',
            value=f'{self._value!r}',
            hint=hint,
            is_valid=self._is_valid
        )

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} ' \
               f'code={self._code!r}, ' \
               f'param={self._param!r}, ' \
               f'value={self._value!r}, ' \
               f'pattern={self._pattern!r}, ' \
               f'is_valid={self._is_valid}' \
               f'>'


class OpaId(UTMCode):
    _code = 'ID'
    _pattern = CONFIG.parsing.utm_codes_regex.get(_code, r'\d+')
    _hint = 'Only digits expected'


class RegCode(UTMCode):
    _code = 'REG-CODE'
    _pattern = CONFIG.parsing.utm_codes_regex.get(_code, r'\d{2}|111|711|7114')
    _hint = 'Only 2 digits or 111|711|7114 expected'


class MunCode(UTMCode):
    _code = 'MUN-CODE'
    _pattern = CONFIG.parsing.utm_codes_regex.get(_code, r'\d{8}')
    _hint = 'Only 8 digits expected'


class OgrnCode(UTMCode):
    _code = 'OGRN'
    _pattern = CONFIG.parsing.utm_codes_regex.get(_code, r'\d{13}')
    _hint = 'Only 13 digits expected'


class Source(enum.Enum):
    VK = 'vk'
    VK1 = 'vk1'
    VK2 = 'vk2'
    UNDEFINED = None

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.__str__()

    @classmethod
    def get_by_value(cls, value: str) -> 'Source':
        for member_name, member in Source.__members__.items():
            if value == member.value:
                return member
        return Source.UNDEFINED


class PosUrl:
    SPACERS_PATTERN = r'\s|%20'
    TEMPLATE_PATTERN = r'https://pos\.gosuslugi\.ru/' \
                       r'(?:form/\?(opaId=\d+)|og/org-activities\?(?:(reg_code=\d{2}|111|711|7114)|(mun_code=\d{8})))' \
                       r'&(utm_source=vk|utm_source=vk[12])' \
                       r'&(utm_medium=\d{2}|111|711|7114)' \
                       r'&(utm_campaign=\d{13})'

    class StatusType(enum.Enum):
        VALID = CONFIG.display.status_types.items['VALID']
        NOT_MATCH = CONFIG.display.status_types.items['NOT_MATCH']
        UTM_INVALID = CONFIG.display.status_types.items['UTM_INVALID']
        SPACER = CONFIG.display.status_types.items['SPACER']
        UNDEFINED = CONFIG.display.status_types.items['UNDEFINED']

        def __str__(self) -> str:
            return CONFIG.display.status_types.pattern.format(**self.value)

    _path: str = None
    _source: Source = Source.UNDEFINED
    _utm_codes: Dict[str, UTMCode] = {}
    status_type: 'StatusType'

    @property
    def path(self) -> str:
        return self._path

    @property
    def source(self) -> Source:
        return self._source

    @property
    def utm_codes(self) -> Dict[str, UTMCode]:
        return self._utm_codes

    def validate(self, path: str, params: Dict[str, str]) -> 'PosUrl':
        if not self._path == path:
            self.status_type = PosUrl.StatusType.UNDEFINED
        elif not self._check_utm_codes(params):
            self.status_type = PosUrl.StatusType.UTM_INVALID
        elif not self._check_spacers():
            self.status_type = PosUrl.StatusType.SPACER
        elif not self._check_pos_link_template():
            self.status_type = PosUrl.StatusType.NOT_MATCH
        else:
            self.status_type = PosUrl.StatusType.VALID
        return self

    def _check_utm_codes(self, params: Dict[str, str]) -> bool:
        for param, value in params.items():
            if param in self._utm_codes:
                utm_code = self._utm_codes[param]
            else:
                utm_code = UTMCode(code='UNDEFINED')

            utm_code.param = param
            utm_code.value = value
            if param and value:
                self._utm_codes[param] = utm_code

        return all([code.is_valid for code in self._utm_codes.values()])

    def _check_spacers(self) -> bool:
        pattern = re.compile(self.SPACERS_PATTERN)
        match = re.findall(pattern, self.url)
        if not match:
            return True

    def _check_pos_link_template(self) -> bool:
        pattern = re.compile(self.TEMPLATE_PATTERN)
        match = re.fullmatch(pattern, self.url)
        if match:
            return True

    def __init__(self, url: str):
        self.__url = url

    @property
    def url(self) -> str:
        return self.__url

    def __str__(self) -> str:
        return f'<{self.__class__.__name__} ' \
               f'status_types={self.status_type}, ' \
               f'url={self.url!r}' \
               f'>'

    def __repr__(self) -> str:
        return self.__str__()


class FormUrl(PosUrl):
    _path = 'form'
    _source: Source = Source.VK

    def __init__(self, url: str):
        super().__init__(url=url)
        self._utm_codes = {
            'opaId': OpaId(),
            'utm_source': UTMCode(code='SOURCE', hint=f'{self._source!r} expected', pattern=self._source.value),
            'utm_medium': RegCode(),
            'utm_campaign': OgrnCode()
        }


class RoivUrl(PosUrl):
    _path = 'og/org-activities'
    _source: Source = Source.VK1

    def __init__(self, url: str):
        super().__init__(url=url)
        self._utm_codes = {
            'reg_code': RegCode(),
            'utm_source': UTMCode(code='SOURCE', hint=f'{self._source!r} expected', pattern=self._source.value),
            'utm_medium': RegCode(),
            'utm_campaign': OgrnCode()
        }


class OmsuUrl(PosUrl):
    _path = 'og/org-activities'
    _source: Source = Source.VK2

    def __init__(self, url: str):
        super().__init__(url=url)
        self._utm_codes = {
            'mun_code': MunCode(),
            'utm_source': UTMCode(code='utm_source', hint=f'{self._source!r} expected', pattern=self._source.value),
            'utm_medium': RegCode(),
            'utm_campaign': OgrnCode()
        }


class PosWidget:
    BASE_URL = 'https://pos.gosuslugi.ru'
    WIDGETS_CONTAINER_SELECTOR = 'div#group_section_menu_gallery .ui_gallery__inner'
    POS_URL_TYPES = {
        Source.VK: FormUrl,
        Source.VK1: RoivUrl,
        Source.VK2: OmsuUrl,
        Source.UNDEFINED: PosUrl
    }

    class ResultType(enum.Enum):
        CORRECT = CONFIG.display.result_types.items['CORRECT']
        INVALID = CONFIG.display.result_types.items['INVALID']
        LINKS_COUNT = CONFIG.display.result_types.items['LINKS_COUNT']
        MISSING = CONFIG.display.result_types.items['MISSING']
        TIMEOUT = CONFIG.display.result_types.items['TIMEOUT']
        ERROR = CONFIG.display.result_types.items['ERROR']

        def __str__(self) -> str:
            return CONFIG.display.result_types.pattern.format(**self.value)

    urls: List[PosUrl] = []
    result: ResultType = ResultType.ERROR

    @classmethod
    def extract_url_params(cls, url: str) -> Tuple[str, Dict]:
        parsed_url = urlparse(url)
        path = parsed_url.path.strip('/')
        query_params = parse_qs(parsed_url.query, keep_blank_values=True)
        params = {key: value[0] for key, value in query_params.items()}
        return path, params

    def parse_data(self, data: dict) -> 'PosWidget':
        menu = data.get('menu')
        if menu:
            self.urls = [
                self.get_validated_pos_url(item)
                for item in menu['items']
                if item['url'].startswith(self.BASE_URL)
            ]

        self.result = self._get_result()
        return self

    def get_validated_pos_url(self, item: Dict) -> PosUrl:
        url = item['url']
        path, params = self.extract_url_params(url)
        utm_source = params.get('utm_source')
        if utm_source:
            source = Source.get_by_value(utm_source)
            pos_url = self.POS_URL_TYPES[source](url=url)
        else:
            pos_url = PosUrl(url)
        pos_url.validate(path, params)
        return pos_url

    def _get_result(self, urls: List[PosUrl] = None) -> ResultType:
        urls = self.urls if not urls else urls

        if not urls:
            return self.ResultType.MISSING

        if CONFIG.parsing.max_links_per_widget != 0 and len(urls) != CONFIG.parsing.max_links_per_widget:
            return self.ResultType.LINKS_COUNT

        if all([pos_url.status_type == PosUrl.StatusType.VALID for pos_url in urls]):
            return self.ResultType.CORRECT

        if len(list(filter(
                lambda u: u.status_type in (
                        PosUrl.StatusType.NOT_MATCH,
                        PosUrl.StatusType.UTM_INVALID,
                        PosUrl.StatusType.SPACER,
                        PosUrl.StatusType.UNDEFINED
                ), urls
        ))) > 0:
            return self.ResultType.INVALID

        return self.ResultType.ERROR
