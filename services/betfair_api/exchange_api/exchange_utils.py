from typing import Any, Callable, Dict, TypeGuard


class ExchangeUtils:
    @staticmethod
    def divisor(entrance_list: list, partition: int) -> tuple[int, int]:
        list_lenght = len(entrance_list)

        N = int(list_lenght / partition)
        N2 = list_lenght - N * partition

        return N, N2

    @staticmethod
    def get_runner_name(runner_list, market_id: str, selection_id: int) -> str:
        filter_lambda = lambda x: x['market_id'] == market_id and x['selection_id'] == selection_id
        runner = list(filter(filter_lambda, runner_list))
        if len(runner) == 0:
            return ''
        return f" {runner[0]['runner_name']}"
