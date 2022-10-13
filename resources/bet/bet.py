from typing import Dict, List

import pandas as pd
from resources.data_treatment import DataFrameParser
from services.betfair_api import BetAPI

from .bet_model import *


class Bet(BetAPI):
    @staticmethod
    def bet_body_builder(data: pd.DataFrame) -> List[BetBody]:
        result: List[BetBody] = []
        for i, row in data.iterrows():
            market_id, selection_id = '', ''
            result.append(BetBody(
                market_id=market_id,
                instructions=BetInstructions(

                )
            ))

    def __init__(self,):
        self.dataframe = DataFrameParser()
        self.df = self.dataframe.df

    def create_bets(self, ):
        ...
