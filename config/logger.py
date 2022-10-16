import logging

logging.basicConfig(level=logging.INFO)


class Logger:
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        logger = logging.getLogger(name)
        return logger
