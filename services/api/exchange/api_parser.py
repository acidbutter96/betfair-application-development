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

    def request_list_builder(self, request_list:list, event_ids_list:str, partition:int, endpoint:str, params:dict)->tuple:
        request_list.append([self.request_builder(endpoint,
                params(id),
                id) for id in event_ids_list[:partition]])
        event_ids_list = event_ids_list[partition:]

        return request_list, event_ids_list


    def competition_partition_rpc(self, soccer_events:list, partition:int=100):
        event_ids_list = [x["event_id"] for x in soccer_events]
        events_lenght = len(event_ids_list)
        output = []
        not_found_competition_ids = []
        
        N = int(events_lenght / partition)
        N2 = events_lenght - N * partition
        
        request_list = []

        params = lambda id: {"filter": {"eventIds": [id]}}

        for n in range(N):
            request_list, event_ids_list = self.request_list_builder(request_list, event_ids_list, partition, "listCompetitions", params)
    
        if len(event_ids_list) == N2 and N2!=0:
            request_list, event_ids_list = self.request_list_builder(request_list, event_ids_list, partition, "listCompetitions", params)
        i=0
        for group in request_list:
            # aux_response = []
            res = self.json_rpc_req(group)[0]
            output = [*output, *res]
        not_found_competition_ids = []
        final_output = []
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
