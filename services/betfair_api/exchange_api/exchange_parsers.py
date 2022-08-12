from typing import Any, Callable, Dict, List, Tuple, TypeGuard

from services.betfair_api.exchange_api.exchange_utils import ExchangeUtils
from services.betfair_api.requests import RequestAPI

from .exchange_builders import ExchangeBuilders


class ExchangeParsers(RequestAPI, ExchangeBuilders, ExchangeUtils):

    def __init__(self, name: str,
                 password: str, x_application_id: str
                 ):
        super(RequestAPI, self).__init__(name, password, x_application_id)
        super(ExchangeBuilders, self).__init__()
        super(ExchangeUtils, self).__init__()

    def request_list_builder(self, request_list: List,
                             to_process_list: List, partition: int,
                             endpoint: str, params: Callable,
                             new_id: Callable = lambda x: None
                             ) -> tuple:
        id_parser = lambda id: new_id(id) if new_id(None) != None else id

        request_list.append([self.request_builder(endpoint,
                                                  params(id),
                                                  id_parser(id)) for id in to_process_list[:partition]])
        to_process_list = to_process_list[partition:]

        return request_list, to_process_list

    def request_partition_controller(
        self, entry_list: list,
        partition: int, request: str,
        params: Callable, new_id: Callable = lambda x: None
    ):
        request_list: List[dict] = []
        N, N2 = self.divisor(entry_list, partition)

        for _ in range(N):
            request_list, entry_list = self.request_list_builder(
                request_list, entry_list,
                partition, request,
                params, new_id
            )

        if len(entry_list) == N2 and N2 != 0:
            request_list, entry_list = self.request_list_builder(
                request_list, entry_list,
                partition, request,
                params, new_id
            )

        return request_list, entry_list

    def process_queue(
        self, request_list: list,
        builder: Callable, builder_args_lambda: Callable,
    ):
        not_found_ids: List[dict] = []
        output_builder: List[dict] = []
        output: List[dict] = []

        for group in request_list:
            res = self.json_rpc_req(group)[0]
            output_builder = [*output_builder, *res]
        for out in output_builder:
            if "result" in out.keys():
                if len(out["result"]) != 0:
                    output.append(
                        builder(*builder_args_lambda(out))
                    )
                elif "id" in out.keys():
                    not_found_ids.append(out["id"])
                else:
                    print(f"Look after\n {out}")
            elif "id" in out.keys():
                not_found_ids.append(out)
            else:
                print(f"Look after\n {out}")
        return output, not_found_ids

    def competition_partition_rpc(self, soccer_events: list,
                                  partition: int = 100
                                  ):
        event_ids_list = [x["event_id"] for x in soccer_events]

        params = lambda id: {"filter": {"eventIds": [id]}}

        request_list, event_ids_list = self.request_partition_controller(
            event_ids_list, partition,
            "listCompetitions", params
        )
        builder_lambda = lambda out: (out['result'][0], out['result'])

        return self.process_queue(
            request_list, self.competition_list_builder,
            builder_args_lambda=builder_lambda
        )

    def market_list_partition_rpc(self, soccer_events: list,
                                  partition: int = 100
                                  ):
        event_ids_list = [x["event_id"] for x in soccer_events]

        params = lambda id: {
            "filter": {
                "eventIds": [id],
            },
            "marketProjection": [
                "COMPETITION",
                "EVENT",
                "EVENT_TYPE",
                "RUNNER_DESCRIPTION",
                "RUNNER_METADATA",
                "MARKET_START_TIME"
            ],
            "maxResults": 1000
        }

        builder_lambda = lambda out: (out["result"], out["id"], 'i')

        request_list, event_ids_list = self.request_partition_controller(
            event_ids_list, partition,
            "listMarketCatalogue", params
        )

        return self.process_queue(request_list, self.market_list_builder,
                                  builder_args_lambda=builder_lambda)

    def market_catalogue_list_partition_rpc(self, market_catalogue_list,
                                            partition: int = 100
                                            ):
        market_list = []

        def params(market): return {
            "marketIds": [market['market_id']],
            "priceProjection": {
                "priceData": ["EX_ALL_OFFERS"],
            }
        }

        id_parser = lambda market: f"{market['market_name']}_~_{market['market_id']}" if market != None else None

        builder_lambda = lambda out: (out["result"][0], out["id"])

        for x in market_catalogue_list:
            for y in x["list"]:
                market_list.append({
                    "market_id": y["marketId"],
                    "market_name": y["marketName"]
                })

        request_list, market_list = self.request_partition_controller(
            market_list, partition,
            "listMarketBook", params, id_parser
        )

        return self.process_queue(request_list,
                                  self.market_book_builder,
                                  builder_args_lambda=builder_lambda)

    def runners_list_getter(
        self, market_catalogue_list,
    ) -> List[dict]:
        runners: List[dict] = []
        aux_runners: List[Dict[str, str]] = []
        market_ids_list: List[str] = []
        not_found: List[str] = []
        for event in market_catalogue_list:
            for market in event["list"]:
                if market["marketId"] not in market_ids_list:
                    market_ids_list.append(market["marketId"])
                new_runners = [
                    self.runner_list_builder(
                        runner,
                        market['marketId']
                    ) for runner in market['runners']
                ]
                aux_runners = [*aux_runners, *new_runners]

        for market_id in market_ids_list:
            filter_by_market_id = lambda x: market_id == x['market_id']
            filtered_by_mk_id = list(
                filter(
                    filter_by_market_id,
                    aux_runners
                )
            )
            if len(filtered_by_mk_id) > 0:
                runners.append({
                    "market_id": market_id,
                    "runners": [
                        {
                            "selection_id": x["selection_id"],
                            "runner_name": x["runner_name"],
                        } for x in filtered_by_mk_id
                    ]
                }
                )
            else:
                not_found.append(market_id)

        return runners
