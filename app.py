import asyncio

from config import Logger, config
from resources.bet import Bet
from resources.data_treatment import DataFrameParser


class BetfairApplication:
    def __init__(self,):
        self.data_frame_parser = DataFrameParser(
            config.NAME, config.PASSWORD, config.X_APPLICATION_ID
        )
        self.logger = Logger().get_logger("Betfair application")

    def load_from_api(self,):
        self.data_frame_parser.get_data_from_api()
        self.data_frame_parser.first_cycle()
        asyncio.run(self.data_frame_parser.second_cycle())
        self.data_frame_parser.third_cycle()
        self.data_frame_parser.to_csv()
        self.df = self.data_frame_parser.df

    def load_from_csv(self, file_name: str) -> None:
        self.logger.info(f"Loading from ./output/{file_name}")
        self.df = self.data_frame_parser.load_from_csv(file_name)
