from services.api import BetAPI

from .data_treatment import DataFrameParser


class Bet(BetAPI):
    def __init__(self,):

        self.dataframe = DataFrameParser()
        ...
    ...
