from services.api.requests import RequestAPI


class ApiParser(RequestAPI):
    @staticmethod
    def soccer_event_list_builder(event) -> dict:
        event_keys = list(event.keys())
        has_event = event_keys.count("event") == 1

        has_mkt_count = list(event_keys).count("marketCount") == 1
        data = {}

        if has_event:
            event_e_keys = list(event["event"].keys())
            has_country_code = event_e_keys.count("countryCode") == 1
            data["event_id"] = event["event"]["id"]
            data["teams_name"] = event["event"]["name"].split(" v ")
            data["event_timezone"] = event["event"]["timezone"]
            data["event_open_date"] = event["event"]["openDate"]
            if has_country_code:
                data["event_country_code"] = event["event"]["countryCode"]
            if has_mkt_count:
                data["event_market_count"] = event["marketCount"]
        return data

    @staticmethod
    def competition_list_builder(competition, id) -> dict:
        comp_keys = list(competition.keys())
        has_comp = comp_keys.count("competition") == 1
        has_mkt_count = comp_keys.count("marketCount") == 1
        has_comp_reg = comp_keys.count("competitionRegion") == 1

        data = {}
        data["event_id"] = id
        if has_comp:
            data["competition_id"] = competition["competition"]["id"]
            data["competition_name"] = competition["competition"]["name"]
        if has_mkt_count:
            data["competition_market_count"] = competition["marketCount"]
        if has_comp_reg:
            data["competition_region"] = competition["competitionRegion"]
        return data

    @staticmethod
    def market_list_builder(market, id, runners) -> dict:
        data = {}
        data["event_id"] = id
        data["list"] = market
        data["runners"] = runners
        return data

    @staticmethod
    def market_book_builder(runner, id) -> dict:
        data = {}
        data["market_name_id"] = id
        data["status"] = runner["status"]
        data["inplay"] = runner["inplay"]
        data["numberOfActiveRunners"] = runner["numberOfActiveRunners"]
        data["totalAvailable"] = runner["totalAvailable"]
        # data["totalMatched"] = runner["totalMatched"]
        # data["numberOfWinners"] = runner["numberOfWinners"]
        # data["complete"] = runner["complete"]
        # data["crossMatching"] = runner["crossMatching"]
        data["runners"] = runner["runners"]
        # data["list"] = runner
        return data

    @staticmethod
    def request_builder(endpoint:str, params:dict, id:str):
            return {
                "jsonrpc": "2.0",
                "method": f"SportsAPING/v1.0/{endpoint}",
                "params": {
                    **params
                },
                "id": id
            }

    def __init__(self, name:str, password:str, x_application_id:str):
        super().__init__(name, password, x_application_id)

    def request_list_builder(self, request_list:list, to_process_list:str,
    partition:int, endpoint:str, params:any, new_id:any=None)->tuple:
        
        id_parser = lambda id: new_id(id) if new_id!=None else id

        request_list.append([self.request_builder(endpoint,
                params(id),
                id_parser(id)) for id in to_process_list[:partition]])
        to_process_list = to_process_list[partition:]

        return request_list, to_process_list

    def competition_partition_rpc(self, soccer_events:list, partition:int=100):
        event_ids_list = [x["event_id"] for x in soccer_events]
        events_lenght = len(event_ids_list)
        output = []
        not_found_competition_ids = []
        
        N = int(events_lenght / partition)
        N2 = events_lenght - N * partition
        
        request_list = []
        not_found_competition_ids = []
        final_output = []

        params = lambda id: {"filter": {"eventIds": [id]}}

        for n in range(N):
            request_list, event_ids_list = self.request_list_builder(request_list, event_ids_list,
            partition, "listCompetitions", params)
    
        if len(event_ids_list) == N2 and N2!=0:
            request_list, event_ids_list = self.request_list_builder(request_list, event_ids_list,
            partition, "listCompetitions", params)

        for group in request_list:
            # aux_response = []
            res = self.json_rpc_req(group)[0]
            output = [*output, *res]
        for e in output:
            if len(e["result"]) != 0:
                final_output.append(
                    self.competition_list_builder(e["result"][0], e["id"])
                )
            else:
                not_found_competition_ids.append(e["id"])
        return final_output, not_found_competition_ids

    def market_list_partition_rpc(self, soccer_events:list, partition:int=100):
        event_ids_list = [x["event_id"] for x in soccer_events]
        events_lenght = len(event_ids_list)
        request_list = []
        output = []
        not_founded_market_ids = []        

        N = int(events_lenght / 100)
        N2 = events_lenght - N * 100

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

        for n in range(N):
            request_list, event_ids_list = self.request_list_builder(request_list, event_ids_list,
                    partition, "listMarketCatalogue",
                    params
                )

        if len(event_ids_list) == N2 and N2 != 0:
            request_list, event_ids_list = self.request_list_builder(request_list, event_ids_list,
                    partition, "listMarketCatalogue",
                    params
                )

        for group in request_list:
            res = self.json_rpc_req(group)[0]
            output = [*output, *res]

        not_founded_market_ids = []
        self.outputt = output
        final_output = []
        for e in output:
            if len(e['result']) != 0:
                final_output.append(
                    self.market_list_builder(e["result"], e["id"],'i'))
            else:
                not_founded_market_ids.append(e["id"])

        return final_output, not_founded_market_ids

    def market_catalogue_list_partition_rpc(self,  market_catalogue_list, partition:int=100):
        market_list = []
        for x in market_catalogue_list:
            for y in x["list"]:
                market_list.append({
                    "market_id":y["marketId"],
                    "market_name":y["marketName"]
                    })

        markets_lenght = len(market_list)
        request_list = []
        output = []
        not_founded_market_books = []

        N = int(markets_lenght / partition)
        N2 = markets_lenght - N * partition

        params = lambda market: {
                    "marketIds": [market['market_id']],
                    "priceProjection": {
                        "priceData":["EX_ALL_OFFERS"],
                        }               
                    }
        id_parser = lambda market: f"{market['market_name']}_~_{market['market_id']}"

        for n in range(N):
            request_list, market_list = self.request_list_builder(request_list, market_list,
            partition, "listMarketBook", params, id_parser)

        if len(market_list) == N2  and N2 != 0:

            request_list, market_list = self.request_list_builder(request_list, market_list,
            partition, "listMarketBook", params, id_parser)
        self.teste = request_list

        for group in request_list:
            res = self.json_rpc_req(group)[0]
            output = [*output, *res]
        final_output = []

        for e in output:
            if len(e["result"]) != 0:
                final_output.append(
                    self.market_book_builder(e["result"][0], e["id"]))
            else:
                not_founded_market_books.append(e["id"])
        return final_output, not_founded_market_books
