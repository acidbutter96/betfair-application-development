from typing import List

import pandas as pd
from resources.data_treatment import DataFrameParser
from services.betfair_api import BetAPI

from .bet_models import *


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
            id = f"{row['event_id']}~{row['selection_id']}"
            market_id = row['market_id']
            selection_id = row['selection_id']
            result.append(
                BetBody(
                    id=id,
                    marketId=market_id,
                    instructions=BetInstructions(
                        selectionId=selection_id, handicap=handicap,
                        side=side, orderType=order_type,
                        limitOrder=LimitOrder(
                            size=size, price=price,
                            persistenceType=persistence_type
                        ),
                    )
                )
            )
        return result

    def __init__(
        self, side: str,
        handicap: str, size: str,
        price: str, data_frame: pd.DataFrame,
        persistence_type: str = "LAPSE", order_type: str = "LIMIT",
    ):
        self.side = side
        self.order_type = order_type
        self.handicap = handicap
        self.size = size
        self.price = price
        self.persistence_type = persistence_type
        self.df: pd.DataFrame = data_frame

    def create_bets_list(
        self, size: str,
        price: str, side: str,
        order_type: str = "LIMIT", handicap: str = "0",
        persistence_type: str = "LAPSE",
    ):
        self.bet_list = self.bet_body_builder(
            side=side, order_type=order_type, handicap=handicap,
            size=size, price=price,
            persistence_type=persistence_type, data=self.df,
        )
        return self.bet_on(self.bet_list)
