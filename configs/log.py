import logging

from . import CONFIG

APP_NAME = 'find-pos-widgets'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
LOG_FORMAT = f'%(asctime)s.%(msecs)-3d - {APP_NAME} - %(levelname)-8s - %(threadName)s -' \
             ' %(name)s.%(funcName)s(line%(lineno)d): %(message)s'
LOG_FILE_FORMATTER = logging.Formatter(
    fmt=LOG_FORMAT,
    datefmt=LOG_DATE_FORMAT,
)


def setup():
    logging.basicConfig(
        format=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT,
        level=logging.DEBUG,
        handlers=[get_runtime_handler()]
    )

    loggers = ['selenium', 'urllib3']
    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.ERROR)

    add_thread_name_to_log_format()


def add_thread_name_to_log_format():
    current_formatter = logging.getLogger().handlers[0].formatter
    new_format = current_formatter._fmt.replace('%(threadName)s', '%(threadName)s')
    new_formatter = logging.Formatter(fmt=new_format, datefmt=LOG_DATE_FORMAT)
    current_handler = logging.getLogger().handlers[0]
    current_handler.setFormatter(new_formatter)


def get_runtime_handler():
    runtime_handler = logging.FileHandler(filename=CONFIG.paths.log_file, encoding='utf-8')
    runtime_handler.setFormatter(LOG_FILE_FORMATTER)
    runtime_handler.setLevel(level=logging.DEBUG)
    return runtime_handler


def get_logger(name: str = __name__) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    return logger


setup()
