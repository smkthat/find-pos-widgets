import json
import sys
import time
import unicodedata
from typing import Set, Dict, List
from urllib.parse import urlparse

from tqdm import tqdm
from vk import API
from vk.exceptions import VkAPIError
from requests.exceptions import ConnectionError

from configs import CONFIG
from configs import get_logger
from finder import Public, PosWidget
from helpers import split_dict_by_keys

logger = get_logger(__name__)


class WidgetFinder:
    VK_BASE_URL = 'https://vk.com'

    urls: Set[str]
    publics: Dict[str, Public]
    __api: API

    def __init__(self):
        self.urls = set()
        self.publics = {}
        self.__counters = {result_type.name: 0 for result_type in PosWidget.ResultType}
        self.__api = API(access_token=CONFIG.vk_api['access_token'], v=CONFIG.vk_api.get('version', '5.131'))
        self.csv_header = self.get_csv_header()

    def get_csv_header(self) -> str:
        header = ''
        for field in CONFIG.display.public_display_fields:
            if field == 'pos_links':
                for i in range(1, CONFIG.parsing.max_links_per_widget + 1):
                    header += f'pos_link{i}' \
                              f'{CONFIG.display.csv_delimiter}' \
                              f'pos_link{i}_status' \
                              f'{CONFIG.display.csv_delimiter}'
            else:
                header += f'{field}{CONFIG.display.csv_delimiter}'
        return header[:-1]

    @property
    def api(self):
        return self.__api

    def start(self) -> None:
        self.clear_resources()
        self.read_urls_from_file()
        self.process_publics()

    def clear_resources(self) -> None:
        logger.info(f'Clearing resources ...')
        print(f'Clearing resources ...')
        open(CONFIG.paths.log_file, 'w', encoding='utf-8').close()
        with open(CONFIG.paths.result_file, 'w', encoding='utf-16') as f:
            f.write(self.csv_header)

    def read_urls_from_file(self) -> None:
        logger.info('Reading file ...')
        print('Reading file ...')
        try:
            with open(CONFIG.paths.target_file, 'r', encoding='utf-8') as file:
                self.urls = self.clean_urls(file.read().splitlines())
                if not self.urls:
                    logger.error(f'No links found in file {CONFIG.paths.target_file!r}.')
                    print(f'No links found in file {CONFIG.paths.target_file!r}.')
                    exit(1)
                else:
                    logger.info('Prepare publics from links ...')
                    print('Prepare publics from links ...')
                    for url in self.urls:
                        if url not in self.publics:
                            self.publics[url] = Public(url)
        except FileNotFoundError:
            open(CONFIG.paths.target_file, 'w', encoding='utf-8').close()
            logger.error(f'File with links not found: {CONFIG.paths.target_file!r}')
            print(f'File with links not found: {CONFIG.paths.target_file!r}')
            exit(2)
        finally:
            logger.info(f'Number of links found: {len(self.urls)}')
            print(f'Number of links found: {len(self.urls)}')

    def process_publics(self) -> None:
        logger.info('Start processing:')
        print('Start processing:')

        publics_group = split_dict_by_keys(self.publics)

        with tqdm(
                total=len(self.urls),
                ncols=150,
                desc='Processing',
                unit='url',
                mininterval=CONFIG.progressbar.min_interval_per_unit,
        ) as pbar:
            pbar.set_postfix(self.__counters)
            for publics in publics_group:
                publics_data_list = publics.values()
                try:
                    publics_data_list = self.__get_publics_data(
                        group_identifies=[p.identify for p in publics_data_list]
                    )
                    pbar.set_postfix(self.__counters)
                except VkAPIError as ve:
                    sys.exit(f'{type(ve).__name__}: {ve}')
                except ConnectionError as ce:
                    for p in publics_data_list:
                        p.pos_widget.result = PosWidget.ResultType.TIMEOUT
                    logger.error(f'Raised exception during handle {str(publics.keys())}:\n{type(ce)} {ce}')
                except RuntimeError as e:
                    for p in publics_data_list:
                        p.pos_widget.result = PosWidget.ResultType.ERROR
                    logger.error(f'Raised exception during handle {str(publics.keys())}:\n{type(e)} {e}')
                finally:
                    for public_data in publics_data_list:
                        if isinstance(public_data, dict):
                            public = self.get_public(public_data)
                            if public:
                                public.parse(public_data)
                            else:
                                public = Public(f'https://vk.com/{public_data.get("screen_name")}')
                                public.pos_widget.result = PosWidget.ResultType.ERROR
                        else:
                            public: Public = public_data

                        self.__save_results_to_file(public)
                        self.__increment_counter(public.pos_widget.result)

                        pbar.set_postfix(self.__counters)
                        pbar.update(1)

                        sleep = CONFIG.progressbar.min_interval_per_unit
                        if sleep and sleep > 0:
                            time.sleep(sleep)

        logger.info(f'Processing complete! {self.__counters}')
        print(f'Processing complete! See results in {CONFIG.paths.result_file!r}')

    def __get_publics_data(
            self,
            group_identifies: List[str],
            tries: int = 0,
            timeout: int = CONFIG.exceptions.get('connection', {}).get('timeout', 5)
    ) -> List[dict]:
        group_ids = ','.join(group_identifies)
        fields = CONFIG.parsing.public_data_fields

        try:
            logger.debug(f'Get data for publics: {group_ids}')
            publics_data = self.api.groups.getById(
                group_ids=group_ids,
                fields=','.join(fields)
            )
        except ConnectionError as ce:
            if tries == CONFIG.exceptions.get('connection', {}).get('max_tries', 5):
                raise ce

            tries += 1
            timeout = timeout * tries

            logger.error(f'{type(ce)}: Can\'t get public data, timeout {timeout} sec: '
                         f'tries={tries}, group_identifies={str(group_identifies)}')
            print(f'\n{type(ce).__name__}: Can\'t get public data, timeout {timeout} sec: : '
                  f'tries={tries}, urls={len(group_identifies)}. '
                  f'For more detail see {CONFIG.paths.result_file!r}.')

            time.sleep(timeout)
            return self.__get_publics_data(group_identifies, tries)
        return publics_data

    def get_public(self, public_data: dict) -> Public:
        by_club = self.publics.get(f'{self.VK_BASE_URL}/club{public_data["id"]}')
        by_public = self.publics.get(f'{self.VK_BASE_URL}/public{public_data["id"]}')
        by_screen_name = self.publics.get(f'{self.VK_BASE_URL}/{public_data.get("screen_name", "")}')
        return by_club if by_club else (by_public if by_public else by_screen_name)

    def __increment_counter(self, counter_type: PosWidget.ResultType) -> None:
        self.__counters[counter_type.name] += 1

    def __save_results_to_file(self, public: Public, result_path: str = 'result.csv') -> None:
        pos_widget = public.pos_widget
        if CONFIG.parsing.skip_correct and pos_widget.result is PosWidget.ResultType.CORRECT:
            pass
        else:
            with open(result_path, 'a', encoding='utf-16') as output:
                result_text = '\n'
                for field in CONFIG.display.public_display_fields:
                    if field == 'pos_links':
                        if pos_widget:
                            result_text += CONFIG.display.csv_delimiter.join([
                                f'{pos_link.url}{CONFIG.display.csv_delimiter}{pos_link.status}'
                                for pos_link in pos_widget.urls
                            ])
                    elif field == 'result':
                        result_text += str(pos_widget.result)
                    elif field == 'url':
                        result_text += public.url
                    else:
                        result_text += str(public.data.get(field, ''))

                    result_text += CONFIG.display.csv_delimiter

                result_text = result_text[:-1]
                logger.info(f'Save result: {result_text!r}')
                output.write(result_text)

        if CONFIG.parsing.save_public_data and public.data:
            with open(f'{CONFIG.paths.save_public_data_dir}/{public.identify}.json', 'w', encoding='utf-8') as f:
                json.dump(public.data, f, ensure_ascii=False)

    def clean_urls(self, urls: List[str]) -> Set[str]:
        return {self.clean_url(url) for url in urls}

    @classmethod
    def clean_url(cls, url: str) -> str:
        url = url.strip('\ufeff')
        url = unicodedata.normalize('NFKC', url.strip())
        parsed_url = urlparse(url)

        scheme = parsed_url.scheme
        if scheme == 'http':
            scheme = 'https'
        hostname = parsed_url.hostname
        if hostname != 'vk.com':
            hostname = 'vk.com'

        url = f'{scheme}://{hostname}{parsed_url.path}'
        return url


if __name__ == '__main__':
    widget_finder = WidgetFinder()
    widget_finder.start()
