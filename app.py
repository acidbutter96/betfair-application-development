import asyncio
import time

from config import Logger, config
from resources.bet import Bet
from resources.data_treatment import DataFrameParser
from utils.chronos import chronometer

betfair_application_logger = Logger().get_logger("betfair_application_logger")


class BetfairApplication:
    def __init__(self,):
        self.data_frame_parser = DataFrameParser(
            config.NAME, config.PASSWORD, config.X_APPLICATION_ID
        )
        self.loaded_from_api = False
        self.loaded_from_csv = False

    def load_from_api(self,) -> DataFrameParser:
        start = time.time()
        self.data_frame_parser.get_data_from_api()
        self.data_frame_parser.first_cycle()
        asyncio.run(self.data_frame_parser.second_cycle())
        self.data_frame_parser.third_cycle()
        self.data_frame_parser.to_csv()
        self.df = self.data_frame_parser.df
        betfair_application_logger.info(
            f"Data acquirement proccess completed on {chronometer(start)}"
        )
        self.loaded_from_api = True
        self.loaded_from_csv = False
        return self.data_frame_parser

    def load_from_csv(self, file_name: str) -> DataFrameParser:
        betfair_application_logger.info(
            f"Loading from ./output/{file_name}")
        self.df = self.data_frame_parser.load_from_csv(file_name)
        self.loaded_from_csv = True
        self.loaded_from_api = False
        return self.data_frame_parser

    def save_excel(self,) -> None:
        if not self.loaded_from_csv and self.loaded_from_api:
            betfair_application_logger.info("Saving excel file")
            self.data_frame_parser.to_xlsx()
        else:
            betfair_application_logger.error(
                "Cannot save an excel file if the data was not loaded from api - run the load_from_api method"
            )
