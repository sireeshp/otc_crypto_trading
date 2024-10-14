import logging
from logging import Logger


def setup_logger(name, log_file, level=logging.INFO) -> Logger:
    """Function to setup a logger."""
    handler = logging.FileHandler(log_file)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger
