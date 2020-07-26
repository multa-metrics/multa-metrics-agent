import sys
import json

from src.handlers.logging_handler import Logger

logs_handler = Logger()
logger = logs_handler.get_logger()


def flatten_dictionary(dd, separator="_", prefix=""):
    return (
        {
            prefix + separator + k if prefix else k: v
            for kk, vv in dd.items()
            for k, v in flatten_dictionary(vv, separator, kk).items()
        }
        if isinstance(dd, dict)
        else {prefix: dd}
    )


class ApplicationHandler:
    def __init__(self):
        pass

    @staticmethod
    def application_restart():
        logger.error("OFFLINE REQUEST TRIGGERED - EXITING")
        sys.exit(1)

    @staticmethod
    def application_offline_log():
        logger.error("OFFLINE REQUEST TRIGGERED - LOGGING")


def get_size(bytes_, suffix="B"):
    """
    Scale bytes to its proper format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes_ < factor:
            return f"{bytes_:.2f}{unit}{suffix}"
        bytes_ /= factor


class ApplicationHandler:
    def __init__(self):
        pass

    @staticmethod
    def application_restart():
        logger.error("OFFLINE REQUEST TRIGGERED - EXITING")
        sys.exit(1)

    @staticmethod
    def application_offline_log():
        logger.error("OFFLINE REQUEST TRIGGERED - LOGGING")


def read_file():
    try:
        with open("bandwidth.txt") as file:
            old_data = json.load(file)
        return old_data
    except Exception:
        logger.error("Can't read file bandwith.txt ")


def write_file(data):
    """
    # TODO: put this file in another location
    this funtion manage a file where is saved the last bandwidth, and the time it was taken
    """
    with open("bandwidth.txt", "w") as file:
        json.dump(data, file)
