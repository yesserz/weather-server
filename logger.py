import logging
from colorlog import ColoredFormatter
from config import LoggingConfig


def myLog(name, fname='myGlobalLog.log'):
    logger = logging.getLogger(name)
    logger.setLevel(LoggingConfig.LOGGING_LEVEL)

    # Создаем форматировщик для вывода в консоль
    LOGFORMAT = "%(log_color)s%(levelname)-8s%(reset)s | %(log_color)s%(message)-50s%(reset)s | %(asctime)s - %(name)s"
    formatterConsole = ColoredFormatter(LOGFORMAT, log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    })

    # Создаем форматировщик для вывода в файл
    formatterFile = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Обработчик для файла
    fhan = logging.FileHandler(fname)
    fhan.setLevel(LoggingConfig.LOGGING_LEVEL)
    fhan.setFormatter(formatterFile)
    logger.addHandler(fhan)

    # Обработчик для вывода в консоль
    sh = logging.StreamHandler()
    sh.setLevel(LoggingConfig.LOGGING_LEVEL)
    sh.setFormatter(formatterConsole)
    logger.addHandler(sh)

    # Возвращаем настроенный логгер
    return logger
