import logging
import os
import sys
from datetime import datetime


class Logger:

    def __init__(self,):
        self.file_name: str = f'{datetime.now().isoformat().split("T")[0]}-logs.log'
        try:
            os.mkdir(f"{os.getcwd()}/logs")
        except OSError:
            print(
                f"The output directory already exists or couldn't be created"
            )
        logging.basicConfig(level=logging.INFO)
        # logging.basicConfig(
        #             level=logging.DEBUG,
        #             format=f"%(levelname)-8s: \t %(filename)s %(funcName)s %(lineno)s - %(message)s"
        #         )

        os.open(f'{os.getcwd()}/{self.file_name}', os.O_CREAT)

        logFileFormatter = logging.Formatter(
            fmt=f"%(levelname)s %(asctime)s (%(relativeCreated)d) \t %(pathname)s F%(funcName)s L%(lineno)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        self.fileHandler = logging.FileHandler(
            filename=f"{os.getcwd()}/logs/{self.file_name}"
        )
        self.fileHandler.setFormatter(logFileFormatter)
        self.fileHandler.setLevel(level=logging.INFO)

        self.log_stream_formatter = logging.Formatter(
            fmt=f"%(levelname)-8s %(asctime)s \t %(filename)s @function %(funcName)s line %(lineno)s - %(message)s",
            datefmt="%H:%M:%S"
        )
        self.consoleHandler = logging.StreamHandler(stream=sys.stdout)
        self.consoleHandler.setFormatter(self.log_stream_formatter)
        self.consoleHandler.setLevel(level=logging.DEBUG)

    def get_logger(self, name: str) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.addHandler(self.fileHandler)
        logger.addHandler(self.consoleHandler)

        return logger
