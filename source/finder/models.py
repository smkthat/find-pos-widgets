import re
import enum

from .configs.log import get_logger

logger = get_logger(__name__)


class Public:
    __url: str
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

    def parse(self, data: dict) -> 'Public':
        if not data:
            self.pos_widget.result = PosWidget.ResultType.ERROR
            return self

        self.pos_widget.parse_data(data)
        self.data = data
        return self


class PosUrl:
    class Status(enum.Enum):
        VALID = 'Correct url'
        NOT_MATCH = 'Invalid, url dont match pattern'
        UTM_INVALID = 'Invalid UTM code value'
        SPACER = 'Invalid, url contains spaces'

        def __str__(self):
            return f'<{self.__class__.__name__} ' \
                   f'name={self.name!r}, ' \
                   f'value={self.value!r}' \
                   f'>'

    def __init__(self, url: str, status: Status = Status.NOT_MATCH):
        self.__url = url
        self.status = status

    @property
    def url(self) -> str:
        return self.__url

    def __str__(self) -> str:
        return f'<{self.__class__.__name__} ' \
               f'status={self.status}, ' \
               f'url={self.url!r}' \
               f'>'


class PosWidget:
    BASE_URL = 'https://pos.gosuslugi.ru'
    WIDGETS_CONTAINER_SELECTOR = 'div#group_section_menu_gallery .ui_gallery__inner'
    UTM_CODES_PATTERN = re.compile(r'REG-CODE|OGRN|ID|MUN-CODE')
    SPACERS_PATTERN = re.compile(r'\s')
    TEMPLATE_PATTERN = re.compile(
        r'https://pos\.gosuslugi\.ru/'
        r'(?:form/\?(opaId=\d+)|og/org-activities\?(?:(reg_code=\d{2,8})|(mun_code=\d{8})))'
        r'&(utm_source=vk|utm_source=vk[12])'
        r'&(utm_medium=\d{2,4})'
        r'&(utm_campaign=\d{13})'
    )

    class ResultType(enum.Enum):
        CORRECT = 'Valid widget urls'
        INVALID = 'Invalid widget urls'
        MISSING = 'Widget not exists'
        TIMEOUT = 'Errors when getting public page data'
        ERROR = 'Runtime errors'

    urls: list[PosUrl]
    result: ResultType

    def __init__(self):
        self.urls = []
        self.result = PosWidget.ResultType.ERROR

    def parse_data(self, data: dict) -> 'PosWidget':
        if menu := data.get('menu'):
            self.urls = [
                self._get_pos_url(item['url'])
                for item in menu['items']
                if item['url'].startswith(self.BASE_URL)
            ]

        self.result = self._get_result()
        return self

    def _get_result(self, urls: list[PosUrl] = None) -> ResultType:
        urls = self.urls if not urls else urls

        if not urls:
            return self.ResultType.MISSING

        if all([pos_url.status == pos_url.Status.VALID for pos_url in urls]):
            return self.ResultType.CORRECT

        if len(list(filter(
                lambda u: u.status in (
                        PosUrl.Status.NOT_MATCH,
                        PosUrl.Status.UTM_INVALID,
                        PosUrl.Status.SPACER
                ), urls
        ))) > 0:
            return self.ResultType.INVALID

        return self.ResultType.ERROR

    def _check_utm_codes(self, url: str) -> bool:
        match = re.findall(self.UTM_CODES_PATTERN, url)
        if not match:
            return True

    def _check_spacers(self, url: str) -> bool:
        match = re.findall(self.SPACERS_PATTERN, url)
        if not match:
            return True

    def _check_pos_link_template(self, url: str) -> bool:
        match = re.fullmatch(self.TEMPLATE_PATTERN, url)
        if match:
            return True

    def _get_pos_url(self, url: str) -> PosUrl:
        if url.startswith(self.BASE_URL):
            if not self._check_utm_codes(url):
                return PosUrl(url, status=PosUrl.Status.UTM_INVALID)

            if not self._check_spacers(url):
                return PosUrl(url, status=PosUrl.Status.SPACER)

            if not self._check_pos_link_template(url):
                return PosUrl(url, status=PosUrl.Status.NOT_MATCH)

            return PosUrl(url, status=PosUrl.Status.VALID)

        return PosUrl(url)


