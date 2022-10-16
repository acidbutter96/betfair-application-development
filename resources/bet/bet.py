import asyncio
from typing import Dict, List

import pandas as pd
from config import config
from resources.data_treatment import DataFrameParser
from services.betfair_api import BetAPI

from .bet_model import *


class Bet(BetAPI):
    @staticmethod
    def bet_body_builder(
        data: pd.DataFrame, side: str,
        order_type: str,
        handicap: str, size: str,
        price: str, persistence_type: str = "LAPSE",
    ) -> List[BetBody]:
        result: List[BetBody] = []
        for i, row in data.iterrows():
            market_id = 'market_id'
            selection_id = 'selection_id'
            result.append(
                BetBody(
                    market_id=market_id,
                    instructions=BetInstructions(
                        handicap=handicap, side=side,
                        order_type=order_type, limit_order=LimitOrder(
                            size=size, price=price,
                            persistence_type=persistence_type
                        )
                    )
                )
            )
        return result

    def __init__(
        self, side: str,
        order_type: str, handicap: str,
        size: str, price: str,
        persistence_type: str = "LAPSE",
    ):
        self.side = side,
        self.order_type = order_type,
        self.handicap = handicap,
        self.size = size,
        self.price = price,
        self.persistence_type = persistence_type,
        self.dataframe = DataFrameParser(
            config.NAME, config.PASSWORD,
            config.X_APPLICATION_ID,
        )
        self.betfair.first_cycle()
        asyncio.run(self.betfair.second_cycle())
        self.betfair.third_cycle()
        self.df = self.dataframe.df

    def create_bets_list(
        self, size: str,
        price: str, persistence_type: str,
        side: str, order_type: str = "LIMIT",
        handicap: str = "0",
    ):
        self.bet_list = self.bet_body_builder(
            side=side, order_type=order_type, handicap=handicap,
            size=size, price=price,
            persistence_type=persistence_type, data=self.df,
        )
        self.bet_on(self.bet_list)
