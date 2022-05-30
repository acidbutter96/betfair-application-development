import time

from services.api.requests import RequestAPI

from .api_parser import ApiParser


class ExchangeAPI(ApiParser):
    def __init__(self, name, password, x_application_id):
        super().__init__(name, password, x_application_id)

    def get_soccer_event_list(self) -> None:
        print("Getting soccer events list\nPOST - listEvents")
        data = {"filter": {"eventTypeIds": ["1"]}}
        try:
            self.soccer_events = []
            for event in self.rest_req("listEvents", data)[0]:
                self.soccer_events.append(
                    self.soccer_event_list_builder(event))
        except Exception as e:
            print(f"Exception {e}")
            return
        print(f"{len(self.soccer_events)} events founded")

    def get_competition_list(self, partition=100) -> None:
        print("Getting competition list...")
        self.competition_list, self.not_found_competition_ids = self.competition_partition_rpc(
            self.soccer_events, partition
        )
        print(f"{len(self.competition_list)} competitions founded\n{len(self.not_found_competition_ids)} competitions not founded")

    def get_market_list(self) -> None:
        print("Getting market catalogue list...")
        event_ids_list = [x["event_id"] for x in self.soccer_events]
        events_lenght = len(event_ids_list)
        request_list = []
        output = []

        def output_list(id):
            return {
                "jsonrpc": "2.0",
                "method": "SportsAPING/v1.0/listMarketCatalogue",
                "params": {
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
                },
                "id": id
            }

        N = int(events_lenght / 100)
        N2 = events_lenght - N * 100

        for n in range(N):
            request_list.append(
                [output_list(id) for id in event_ids_list[:100]])
            event_ids_list = event_ids_list[100:]

        if len(event_ids_list) == N2 and N2 != 0:
            request_list.append([output_list(id) for id in event_ids_list])

        for group in request_list:
            aux_response = []
            res = self.json_rpc_req(group)[0]
            output = [*output, *res]
            """self.request_market_list = request_list
                self.market = output
            """
        self.not_founded_market_ids = []
        self.outputt = output
        final_output = []
        for e in output:
            if len(e['result']) != 0:
                final_output.append(
                    self.market_list_builder(e["result"], e["id"],'i'))
            else:
                self.not_founded_market_ids.append(e["id"])
        self.market_catalogue_list = final_output
        print(f"Found markets from {len(self.market_catalogue_list)} events\n{len(self.not_founded_market_ids)} not founded")

        pass

    def get_market(self,partition=200) -> None:
        start = time.time()
        print("Getting market list...")
        market_list = []
        # y["marketId"] for y in x["list"] for x in self.market_catalogue_list
        for x in self.market_catalogue_list:
            for y in x["list"]:
                market_list.append({
                    "market_id":y["marketId"],
                    "market_name":y["marketName"]
                    })

        markets_lenght = len(market_list)
        request_list = []
        output = []

        def output_list(market):
            return {
                "jsonrpc": "2.0",
                "method": "SportsAPING/v1.0/listMarketBook",
                "params": {
                    "marketIds": [market['market_id']],
                    "priceProjection": {
                        "priceData":["EX_ALL_OFFERS"],
                    }               
                },
                "id": f"{market['market_name']}_~_{market['market_id']}",
            }

        N = int(markets_lenght / partition)
        N2 = markets_lenght - N * partition

        for n in range(N):
            request_list.append(
                [output_list(id) for id in market_list[:partition]])
            market_list = market_list[partition:]
        if len(market_list) == N2  and N2 != 0:
            request_list.append([output_list(market) for market in market_list])

        self.teste = request_list
        for group in request_list:
            res = self.json_rpc_req(group)[0]
            output = [*output, *res]
            """self.request_market_list = request_list
        self.market = output
        """
        self.not_founded_market_books = []
        final_output = []
        for e in output:

            if len(e["result"]) != 0:
                final_output.append(
                    self.market_book_builder(e["result"][0], e["id"]))
            else:
                self.not_founded_market_books.append(e["id"])
        self.market_book_list = final_output
        end = time.time()
        print(f"Found markets from {len(self.market_book_list)} events\n{len(self.not_founded_market_books)} not founded\n Processed in {round(end-start,1)}s")
