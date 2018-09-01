# _*_coding:utf-8_*_

import logging

from conf import settings


def log(log_type):
    LOG_FILE = settings.LOG_FILE

    logger = logging.getLogger(log_type)
    logger.setLevel(settings.LOG_LEVEL)

    ch = logging.StreamHandler()
    fh = logging.FileHandler(LOG_FILE)

    formatter_ch = logging.Formatter("%(asctime)s-%(message)s")
    formatter_fh = logging.Formatter("%(asctime)s- %(name)s- %(levelname)s- %(message)s")

    ch.setFormatter(formatter_ch)
    fh.setFormatter(formatter_fh)

    if logger.handlers:
        return logger

    logger.addHandler(ch)
    logger.addHandler(fh)

    # logger.removeHandler(ch)
    # logger.removeHandler(fh)

    return logger
