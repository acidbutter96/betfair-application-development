from typing import Any, Callable, Dict, TypeGuard

from services.betfair_api import BetfairApiUtils


class ExchangeUtils(BetfairApiUtils):

    @staticmethod
    def get_runner_name(runner_list, market_id: str, selection_id: int) -> str:
        filter_lambda = lambda x: x['market_id'] == market_id and x['selection_id'] == selection_id
        runner = list(filter(filter_lambda, runner_list))
        if len(runner) == 0:
            return ''
        return f" {runner[0]['runner_name']}"
