import logging

log_format = "%(asctime)s [%(levelname)s] - %(name)s - %(funcName)s(%(lineno)d) - %(message)s"

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(logging.Formatter(log_format))


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(stream_handler)
    return logger
