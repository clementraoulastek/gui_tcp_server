import logging
import os


def setup_logger(logger_name):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    )
    # Update the log file
    file_handler = logging.FileHandler(os.path.join(os.getcwd(), logger_name))
    _set_formatter(file_handler, formatter, logger)
    # Update the console
    console_handler = logging.StreamHandler()
    _set_formatter(console_handler, formatter, logger)


def _set_formatter(handler, formatter, logger):
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
