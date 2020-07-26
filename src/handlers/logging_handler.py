import logging
import os


class Logger:
    def __init__(self):
        console_format = "%(pathname)s - %(levelname)s - %(funcName)s - %(lineno)d - %(message)s"
        root = logging.getLogger()
        if root.handlers:
            for handler in root.handlers:
                root.removeHandler(handler)
        logging.basicConfig(format=console_format, level=os.environ.get("LOG_LEVEL", "INFO"))
        self.logger = logging.getLogger()

    def get_logger(self):
        return self.logger
