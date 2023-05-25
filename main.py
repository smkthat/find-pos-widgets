import json
import sys
import time
import unicodedata

from tqdm import tqdm
from vk import API
from vk.exceptions import VkAPIError
from requests.exceptions import ConnectionError

from configs import CONFIG, SAVE_PUBLIC_DATA_DIR, RESULT_FILE_PATH, TARGET_FILE_PATH, LOG_FILE_PATH
from configs import get_logger
from finder import Public, PosWidget
from helpers import split_dict_by_keys

logger = get_logger(__name__)


class WidgetFinder:
    VK_BASE_URL = 'https://vk.com'

    urls: set[str]
    publics: dict[str, Public]
    __api: API

    def __init__(self):
        self.urls = set()
        self.publics = {}
        self.__counters = {result_type.name: 0 for result_type in PosWidget.ResultType}
        self.__api = API(access_token=CONFIG.vk_api['access_token'], v=CONFIG.vk_api.get('version', '5.131'))

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
        open(LOG_FILE_PATH, 'w', encoding='utf-8').close()
        with open(RESULT_FILE_PATH, 'w', encoding='utf-8') as f:
            f.write('pos_result;public_url;pos_link1;pos_link1_status;pos_link2;pos_link2_status\n')

    def read_urls_from_file(self) -> None:
        logger.info('Reading file ...')
        print('Reading file ...')
        try:
            with open(TARGET_FILE_PATH, 'r', encoding='utf-8') as file:
                self.urls = self.clean_urls(file.read().splitlines())
                if not self.urls:
                    logger.error(f'No links found in file {TARGET_FILE_PATH!r}.')
                    print(f'No links found in file {TARGET_FILE_PATH!r}.')
                    exit(1)
                else:
                    logger.info('Prepare publics from links ...')
                    print('Prepare publics from links ...')
                    self.publics = {url: Public(url) for url in self.urls}
        except FileNotFoundError:
            open(TARGET_FILE_PATH, 'w', encoding='utf-8').close()
            logger.error(f'File with links not found: {TARGET_FILE_PATH!r}')
            print(f'File with links not found: {TARGET_FILE_PATH!r}')
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
                mininterval=CONFIG.parsing.get('min_interval', 0.01),
        ) as pbar:
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
                            public.parse(public_data)
                        else:
                            public = public_data

                        self.__save_results_to_file(public)
                        self.__increment_counter(public.pos_widget.result)

                        pbar.set_postfix(self.__counters)
                        pbar.update(1)

                        sleep = CONFIG.parsing.get('min_interval')
                        if sleep and sleep > 0:
                            time.sleep(sleep)

        logger.info('Processing complete!')
        print(f'Processing complete! See results in {RESULT_FILE_PATH!r}')

    def __get_publics_data(
            self,
            group_identifies: list[str],
            tries: int = 0,
            timeout: int = CONFIG.exceptions.get('connection', {}).get('timeout', 5)
    ) -> list[dict]:
        group_ids = ','.join(group_identifies)
        fields = CONFIG.parsing.get('fields', [])
        fields.append('menu')

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
                  f'For more detail see {LOG_FILE_PATH!r}.')

            time.sleep(timeout)
            return self.__get_publics_data(group_identifies, tries)
        return publics_data

    def get_public(self, public_data: dict) -> Public:
        public = self.publics.get(f'{self.VK_BASE_URL}/club{public_data["id"]}') or \
                 self.publics.get(f'{self.VK_BASE_URL}/{public_data.get("screen_name", "")}')
        return public

    def __increment_counter(self, counter_type: PosWidget.ResultType) -> None:
        self.__counters[counter_type.name] += 1

    def __save_results_to_file(self, public: Public, result_path: str = None) -> None:
        if not result_path:
            result_path = RESULT_FILE_PATH

        pos_widget = public.pos_widget
        if not CONFIG.parsing.get('skip_correct') and pos_widget.result is not PosWidget.ResultType.CORRECT:
            with open(result_path, 'a', encoding='utf-8') as output:
                if pos_widget:
                    pos_links_str = ";".join([
                        f'{pos_link.url!r};{pos_link.status}'
                        for pos_link in pos_widget.urls
                    ]) if pos_widget.urls else ';;;'
                    result_text = f'{pos_widget.result.name};{public.url};{pos_links_str}'
                else:
                    result_text = f'{PosWidget.ResultType.ERROR.name};{public.url};;;;'

                logger.info(f'Save result: {result_text!r}')
                output.write(result_text + '\n')

        if SAVE_PUBLIC_DATA_DIR:
            if public.data:
                with open(f'{SAVE_PUBLIC_DATA_DIR}/{public.identify}.json', 'w', encoding='utf-8') as f:
                    json.dump(public.data, f, ensure_ascii=False)

    def clean_urls(self, urls: list[str]) -> set[str]:
        return {self.clean_url(url) for url in urls}

    @classmethod
    def clean_url(cls, url: str) -> str:
        return unicodedata.normalize('NFKC', url)


if __name__ == '__main__':
    widget_finder = WidgetFinder()
    widget_finder.start()
