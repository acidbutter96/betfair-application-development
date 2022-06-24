class ExchangeBuilders:
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
    def market_list_builder(market, id,
        runners
    ) -> dict:
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
    def request_builder(endpoint:str, params:dict,
        id:str
    ) -> dict:
            return {
                "jsonrpc": "2.0",
                "method": f"SportsAPING/v1.0/{endpoint}",
                "params": {
                    **params
                },
                "id": id
            }
