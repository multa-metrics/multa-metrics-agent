import json
import sys
import traceback

from src.handlers.logging_handler import Logger

logs_handler = Logger()
logger = logs_handler.get_logger()


class ApplicationHandler:
    def __init__(self):
        pass

    @staticmethod
    def application_restart() -> None:
        logger.error("OFFLINE REQUEST TRIGGERED - EXITING")
        sys.exit(1)

    @staticmethod
    def application_offline_log() -> None:
        logger.error("OFFLINE REQUEST TRIGGERED - LOGGING")


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


def get_size(bytes_: int, suffix="B") -> str:
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


def read_file():
    try:
        with open("bandwidth.txt") as file:
            old_data = json.load(file)
        return old_data
    except Exception:
        logger.error("Can't read file bandwith.txt ")
        return False


def write_file(data: dict) -> bool:
    """
    This function manage a file where is saved the last bandwidth, and the time it was taken
    """
    try:
        with open("bandwidth.txt", "w") as file:
            json.dump(data, file)
            return True
    except Exception:
        logger.error("Error saving bandwidth data...")
        logger.error(traceback.format_exc())
        return False
