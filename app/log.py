# coding: utf-8

import logging


def _log_init(level):
    # configure log file. Logger is named to avoid other modules, like Camelot, to write into it
    logger = logging.getLogger("mph-tally")
    logger.setLevel(level)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_formatter = logging.Formatter('%(asctime)s :: %(levelname)s :[%(filename)s:%(lineno)d]: %(message)s')
    stream_handler.setFormatter(stream_formatter)
    logger.addHandler(stream_handler)

    return logger


def _std_logger(level):

    if level == 'debug':
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    logger = _log_init(log_level)
    return logger


class Logger:

    __logger_instance = {}

    @classmethod
    def get_logger(cls, app, level):
        if cls.__logger_instance.get(app) is None:
            cls.__logger_instance[app] = _std_logger(level)
        return cls.__logger_instance[app]
