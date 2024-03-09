import logging
from config import LoggingConfig


def myLog(name, fname='myGlobalLog.log'):
    logger = logging.getLogger(name)
    logger.setLevel(LoggingConfig.LOGGING_LEVEL)

    # Создаем форматировщик
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Обработчик для файла
    fhan = logging.FileHandler(fname)
    fhan.setLevel(logging.DEBUG)
    fhan.setFormatter(formatter)
    logger.addHandler(fhan)

    # Обработчик для вывода в консоль
    sh = logging.StreamHandler()
    sh.setLevel(logging.DEBUG)
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    # Возвращаем настроенный логгер
    return logger
