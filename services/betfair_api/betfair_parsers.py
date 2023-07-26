from typing import Callable, List

from services.betfair_api.betfair_requests import RequestAPI


class BetfairApiParsers(RequestAPI):
    def __init__(
        self, name: str,
        password: str, x_application_id: str,
    ):
        super(RequestAPI, self).__init__(name, password, x_application_id)

    def request_list_builder(
        self, request_list: List,
        to_process_list: List, partition: int,
        endpoint: str, params: Callable,
        new_id: Callable = lambda x: None
    ) -> tuple:
        id_parser = lambda id: new_id(id) if new_id(None) != None else id

        request_list.append(
            [
                self.request_builder(
                    endpoint, params(id),
                    id_parser(id),
                )
                for id in to_process_list[:partition]
            ]
        )
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
