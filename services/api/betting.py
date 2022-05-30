from utils.dotenv import CERTNAME

from .exchange import ExchangeAPI


class BetAPI(ExchangeAPI):
    @staticmethod
    def __bet_list_builder(event) -> dict:
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
        ...

    def __init__(self, name, password, x_application_id):
        self.__s.cert = ("./certs/{CERTNAME}.crt", "./certs/{CERTNAME}.pem")
        super().__init__(name, password, x_application_id)
    
    def bet_on(self, bets_list):
        request = super().json_rpc_req()
        ...
