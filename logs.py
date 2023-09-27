import logging


name_to_level = {"DEBUG": logging.DEBUG,
                 "INFO": logging.INFO,
                 "WARN": logging.WARN,
                 "ERROR": logging.ERROR}
LOGLEVEL = 'INFO'
logFormatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')


def setup_logger(name, level=LOGLEVEL):
    """Setup loggers"""
    level = name_to_level[level]
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.hasHandlers():
        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(logFormatter)
        logger.addHandler(consoleHandler)

    return logger
