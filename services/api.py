import json
import os
import time

import requests
from dotenv import load_dotenv
from numpy import outer

load_dotenv()

CERTNAME = os.getenv("CERTNAME")

print(CERTNAME)

class AuthenticationAPI:
    betfair_url = "https://api.betfair.com/v1/account"
    __s = requests.Session()

    def __init__(self, name: str, password: str,
                 x_application_id: str) -> None:
        self.auth_name= name
        self.x_application_id = x_application_id

        url = "https://identitysso-cert.betfair.com/api/certlogin"
        headers = {
            "X-Application": x_application_id,
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {"username": name, "password": password}

        self.__s.cert = (f"./certs/{CERTNAME}.crt",
            f"./certs/{CERTNAME}.pem")
        r = self.__s.post(url=url, data=data, headers=headers)
        self.__auth = r.json()

        print(self.__auth)

        if self.__auth["loginStatus"] == "SUCCESS":
            self.session_token = self.__auth["sessionToken"]
            print(f'User: {data["username"]} is authenticated')
            return None
        if self.__auth["loginStatus"] == "SUSPENDED":
            raise Exception(f'API Error: {self.__auth["loginStatus"]}')
            return None
        raise Exception("Authentication failed, verify your credentials and\
                    try again")

class RequestAPI(AuthenticationAPI):
    __s = requests.Session()
    json_rpc_url = "https://api.betfair.com/exchange/betting/json-rpc/v1"
    REST_url = "https://api.betfair.com/exchange/betting/rest/v1.0/"

    def __init__(self, name, password, x_application_id):
        super().__init__(name, password, x_application_id)
        self.__s.cert = (f"./certs/{CERTNAME}.crt", f"./certs/{CERTNAME}.pem")

    @staticmethod
    def __res_parser(exception, response, error_key):
        if exception != "":
            raise Exception(exception)
        if error_key or response.status_code != 200:
            raise Exception(
                f"Bad request: {exception}\n response code: {response.status_code}\n Body response: {response.content}"
            )
        return response.json(), response.status_code, response.url

    def json_rpc_req(self, data: list) -> tuple:
        request_url = self.json_rpc_url  #+ '{}'.format(operation_name)
        headers = {
            "X-Application": self.x_application_id,
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Authentication": self.session_token
        }

        exception = ""
        try:
            response = self.__s.post(url=request_url,
                                     data=json.dumps(data),
                                     headers=headers)
        except Exception as e:
            exception = str(e)
        return self.__res_parser(exception, response, False)

    def rest_req(self, operation_name: str, data: dict) -> tuple:
        request_url = f"{self.REST_url}{operation_name}/" #+ '{}'.format(operation_name)
        headers = {
            "X-Application": self.x_application_id,
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Authentication": self.session_token
        }
        rb = data
        request_body = json.dumps(rb)
        exception = ""
        try:
            response = self.__s.post(url=request_url,
                                     data=request_body,
                                     headers=headers)
        except Exception as e:
            exception = str(e)
        return self.__res_parser(exception, response, False)

class ExchangeAPI(RequestAPI):
    @staticmethod
    def __soccer_event_list_builder(event) -> dict:
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
    def __competition_list_builder(competition, id) -> dict:
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
    def __market_list_builder(market, id) -> dict:
        data = {}
        data["event_id"] = id
        data["list"] = market
        return data

    @staticmethod
    def __market_book_builder(runner, id) -> dict:
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

    def __init__(self, name, password, x_application_id):
        super().__init__(name, password, x_application_id)

    def get_soccer_event_list(self) -> None:
        print("Getting soccer events list\nPOST - listEvents")
        data = {"filter": {"eventTypeIds": ["1"]}}
        try:
            self.soccer_events = []
            for event in self.rest_req("listEvents", data)[0]:
                self.soccer_events.append(
                    self.__soccer_event_list_builder(event))
        except Exception as e:
            print(f"Exception {e}")
            return
        print(f"{len(self.soccer_events)} events founded")

    def get_competition_list(self, partition=100) -> None:
        print("Getting competition list...")
        event_ids_list = [x["event_id"] for x in self.soccer_events]
        events_lenght = len(event_ids_list)
        request_list = []
        output = []

        #create jsonrpc object
        def output_list(x):
            return {
                "jsonrpc": "2.0",
                "method": "SportsAPING/v1.0/listCompetitions",
                "params": {
                    "filter": {
                        "eventIds": [x]
                    }
                },
                "id": x
            }

        #make json rpc request
        N = int(events_lenght / partition)
        N2 = events_lenght - N * partition
        for n in range(N):
            request_list.append([output_list(x) for x in event_ids_list[:partition]])
            event_ids_list = event_ids_list[partition:]
        if len(event_ids_list) == N2 and N2!=0:
            request_list.append([output_list(x) for x in event_ids_list])
        i=0
        for group in request_list:
            aux_response = []
            res = self.json_rpc_req(group)[0]
            output = [*output, *res]
        self.not_found_competition_ids = []
        final_output = []
        for e in output:
            if len(e["result"]) != 0:
                final_output.append(
                    self.__competition_list_builder(e["result"][0], e["id"]))
            else:
                self.not_found_competition_ids.append(e["id"])
        self.competition_list = final_output
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
                        "eventIds": [id]
                    },
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
        final_output = []
        for e in output:
            if len(e['result']) != 0:
                final_output.append(
                    self.__market_list_builder(e["result"], e["id"]))
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
                    },
                    "marketProjection": [
                            "COMPETITION",
                            "EVENT",
                            "EVENT_TYPE",
                            "RUNNER_DESCRIPTION",
                            "RUNNER_METADATA",
                            "MARKET_START_TIME"
                    ]                
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
                    self.__market_book_builder(e["result"][0], e["id"]))
            else:
                self.not_founded_market_books.append(e["id"])
        self.market_book_list = final_output
        end = time.time()
        print(f"Found markets from {len(self.market_book_list)} events\n{len(self.not_founded_market_books)} not founded\n Processed in {round(end-start,1)}s")

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
