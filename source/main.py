import os
import re
import enum
import concurrent.futures
import threading
import time

from urllib.parse import urlparse

from tqdm import tqdm
from bs4 import BeautifulSoup
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.common.by import By

from configs.log import get_logger, LOG_FILE_PATH

logger = get_logger(__name__)


class ResultType(enum.Enum):
    CORRECT = 'correct'
    NOT_MATCH = 'not_match'
    SPACER = 'spacer'
    COPY_PASTE = 'copy_paste'
    MISSING = 'missing'
    TIMEOUT = 'timeout'
    ERROR = 'error'


class ProcessUrl:
    PAGE_LOAD_TIMEOUT = 10
    RESULT_FILE_PATH = os.path.abspath(os.path.join(os.getcwd(), '../result.csv'))

    result: ResultType = None

    def __init__(self, url: str):
        self.logger = get_logger(__name__)
        self.url = url
        self.__save_lock = threading.Lock()

    def setup_driver(self) -> Chrome:
        options = ChromeOptions()
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-infobars')
        options.add_argument('--dns-prefetch-disable')
        options.add_argument('--ignore-gpu-blacklist')
        options.add_argument('--no-default-browser-check')
        options.add_argument('--no-first-run')
        options.add_argument('--log-level 3')
        options.add_argument('--disable-logging')
        options.add_argument('--disable-in-process-stack-traces')
        options.add_argument('--disable-crash-reporter')
        options.add_argument('--window-size=1024,768')
        options.add_argument('--output=/dev/null')
        options.add_argument('--silent')

        prefs = {'profile.default_content_setting_values': {
            'images': 2,
            'plugins': 2,
        }}
        options.add_experimental_option('prefs', prefs)
        options.add_experimental_option('excludeSwitches', ['enable-logging'])

        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--no-warnings')
        return Chrome(options=options)

    def load_url(self, driver: Chrome, url: str) -> bool:
        try:
            logger.info(f'Processing URL: {url}')
            driver.get(url)
        except WebDriverException as e:
            logger.error(f'Error retrieving page data: {url!r}\n{e.msg}')
            return False

        return True

    def __page_has_loaded(self, driver: Chrome, sleep_time=2) -> bool:
        def get_page_hash(d: Chrome) -> int:
            dom = d.find_element(By.TAG_NAME, 'html').get_attribute('innerHTML')
            dom_hash = hash(dom.encode('utf-8'))
            return dom_hash

        page_hash = -1
        page_hash_new = None
        max_iteration = 10
        iters_count = 0

        while page_hash != page_hash_new:
            if iters_count == max_iteration:
                raise TimeoutException

            page_hash = get_page_hash(driver)
            time.sleep(sleep_time)
            page_hash_new = get_page_hash(driver)
            iters_count += 1

        return True

    def wait_for_page_load(self, driver: Chrome, timeout: float = 5.) -> bool:
        try:
            WebDriverWait(driver, timeout).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            # self.__page_has_loaded(driver, sleep_time=2)
            return True
        except TimeoutException:
            logger.error(f'Page load timeout [{timeout} sec] while processing {self.url!r}')

    def analyze_page(self, html: str) -> ResultType:
        result = ResultType.MISSING
        soup = BeautifulSoup(html, 'html5lib')
        a = soup.find('div', {'id': 'group_section_menu_gallery'})
        if a:
            pos_links = [
                a_tag['href']
                for a_tag in a.find_all('a', {'class': 'groups_menu_item'})
                if a_tag['href'].startswith('https://pos.gosuslugi.ru')
            ]
            if pos_links:
                for template_utm_code in ['REG-CODE', 'OGRN', 'ID', 'MUN-CODE']:
                    if template_utm_code in str(a):
                        result = ResultType.COPY_PASTE
                        self.logger.debug(f'Public {self.url!r}: result={result.name}, pos_links={str(pos_links)}')
                        return result
                    else:
                        if 'mediu m' in str(a):
                            result = ResultType.SPACER
                        elif self.check_widgets_links_template(str(a)):
                            result = ResultType.CORRECT
                        else:
                            result = ResultType.NOT_MATCH

                    self.logger.debug(f'Public {self.url!r}: result={result.name}, pos_links={str(pos_links)}')
                    return result

        self.logger.debug(f'Public {self.url!r}: result={result.name}, pos_links=[]')
        return result

    def process_url(self) -> ResultType:
        driver = self.setup_driver()
        with driver:
            if self.load_url(driver, self.url):
                if self.wait_for_page_load(driver, self.PAGE_LOAD_TIMEOUT):
                    html = driver.page_source
                    self.result = self.analyze_page(html)
            else:
                self.result = ResultType.ERROR

            self.save_results_to_file()
            return self.result

    @property
    def result_text(self) -> str:
        if self.result:
            return f'{self.result.value}; {self.url}'

    def save_results_to_file(self, result_path: str = None) -> None:
        with self.__save_lock:
            if not result_path:
                result_path = self.RESULT_FILE_PATH

            if result_text := self.result_text:
                self.logger.info(f'Save result: {result_text!r}')
                if self.result != ResultType.CORRECT:
                    with open(result_path, 'a', encoding='utf-8') as output:
                        output.write(result_text + '\n')

    def check_widgets_links_template(self, source: str) -> bool:
        template1 = 'https://pos.gosuslugi.ru/form/' + r'.' + \
                    'opaId=' + r'\d+' + \
                    '&amp;utm_source=vk&amp;utm_medium=' + r'\d+' + \
                    '&amp;utm_campaign=' + r'\d+'
        template2 = 'https://pos.gosuslugi.ru/og/org-activities' + r'.' + \
                    'reg_code=' + r'\d+' + \
                    '&amp;utm_source=vk1&amp;utm_medium=' + r'\d+' + \
                    '&amp;utm_campaign=' + r'\d+'
        template3 = 'https://pos.gosuslugi.ru/og/org-activities' + r'.' + \
                    'mun_code=' + r'\d+' + \
                    '&amp;utm_source=vk2&amp;utm_medium=' + r'\d+' + \
                    '&amp;utm_campaign=' + r'\d+'

        matches1 = re.findall(template1, source)
        matches2 = re.findall(template2, source)
        matches3 = re.findall(template3, source)

        return (
                (len(matches1) > 0 and len(matches2) > 0) or
                (len(matches1) > 0 and len(matches3) > 0)
        )


class WidgetFinder:
    TARGET_FILE_PATH = os.path.abspath(os.path.join(os.getcwd(), '../target.txt'))

    def __init__(self):
        self.urls = []
        self.__counters = {result_type.name: 0 for result_type in ResultType}
        self.__counters_lock = threading.Lock()

    def increment_counter(self, counter_type: ResultType) -> None:
        with self.__counters_lock:
            self.__counters[counter_type.name] += 1

    @classmethod
    def check_urls(cls, urls: list) -> list[str]:
        checked_urls = []
        for url in urls:
            if not url.startswith('http'):
                url = 'https://' + url
            parsed_url = urlparse(url)
            if parsed_url.hostname and parsed_url.hostname == 'vk.com':
                checked_urls.append(url)
        return checked_urls

    def read_urls_from_file(self) -> None:
        logger.info('Reading file ...')
        print('Reading file ...')
        try:
            with open(self.TARGET_FILE_PATH, 'r', encoding='utf-8') as file:
                self.urls = self.check_urls(file.read().splitlines())
                if not self.urls:
                    logger.error(f'No links found in file {self.TARGET_FILE_PATH!r}.')
                    print(f'No links found in file {self.TARGET_FILE_PATH!r}.')
                    exit(1)
        except FileNotFoundError:
            open(self.TARGET_FILE_PATH, 'w').close()
            logger.error(f'File with links not found: {self.TARGET_FILE_PATH!r}')
            print(f'File with links not found: {self.TARGET_FILE_PATH!r}')
            exit(2)
        finally:
            logger.info(f'Number of links found: {len(self.urls)}')
            print(f'Number of links found: {len(self.urls)}')

    def __process_url(self, url: str) -> ResultType:
        worker = ProcessUrl(url)
        return worker.process_url()

    def process_urls(self) -> None:
        logger.info('Start processing:')
        print('Start processing:')

        with tqdm(total=len(self.urls), dynamic_ncols=True, desc='Progress', ) as pbar:
            pbar.set_postfix(self.__counters)
            with concurrent.futures.ThreadPoolExecutor(
                    thread_name_prefix='UrlProcessor'
            ) as executor:
                futures = [executor.submit(self.__process_url, url, ) for url in self.urls]
                for future in concurrent.futures.as_completed(futures):
                    result_type = future.result()
                    if isinstance(result_type, ResultType):
                        self.increment_counter(result_type)
                        pbar.set_postfix(self.__counters)
                        pbar.update(1)

        logger.info('Processing complete!')
        print(f'Processing complete! See results in {ProcessUrl.RESULT_FILE_PATH!r}')

    @classmethod
    def clear_resources(cls) -> None:
        open(ProcessUrl.RESULT_FILE_PATH, 'w').close()
        open(LOG_FILE_PATH, 'w').close()

    def start(self) -> None:
        self.read_urls_from_file()
        self.process_urls()


def main():
    WidgetFinder.clear_resources()
    finder = WidgetFinder()
    finder.start()


if __name__ == '__main__':
    main()
