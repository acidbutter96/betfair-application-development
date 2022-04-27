from numpy import outer
import requests
import json
import os


class BetFairAPI:
    betfair_url = 'https://api.betfair.com/v1/account'
    __s = requests.Session()

    def __init__(self, name: str, password: str,
                 x_application_id: str) -> None:
        self.auth_name = name
        self.x_application_id = x_application_id

        url = 'https://identitysso-cert.betfair.com/api/certlogin'
        headers = {
            'X-Application': x_application_id,
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {'username': name, 'password': password}

        self.__s.cert = ('./certs/client-2048.crt', './certs/client-2048.pem')
        r = self.__s.post(url=url, data=data, headers=headers)
        self.__auth = r.json()

        if self.__auth['loginStatus'] == 'SUCCESS':
            self.session_token = self.__auth['sessionToken']
            print('User: {} is authenticated'.format(data['username']))
            return None
        if self.__auth['loginStatus']:
            print('Error: {}'.format(self.__auth['loginStatus']))
            return None
        print('Authentication failed, verify your credentials and try again')


class BettingAPI(BetFairAPI):
    __s = requests.Session()
    json_rpc_url = 'https://api.betfair.com/exchange/betting/json-rpc/v1'
    REST_url = 'https://api.betfair.com/exchange/betting/rest/v1.0/'

    @staticmethod
    def __res_parser(exception, response, error_key):
        if exception != '':
            raise Exception(exception)
            return
        if error_key or response.status_code != 200:
            raise Exception(
                "Bad request\n response code: {}\n Body response: {}".format(
                    response.status_code, response.content, exception))
        return response.json(), response.status_code, response.url

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
        #print('comp {}\n id {}'.format(competition, id))
        #print('comp len{}'.format(len(competition)))
        if len(competition) == 0:
            print('uai {}'.format(competition))
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

    def __init__(self, name, password, x_application_id):
        self.__s.cert = ('./certs/client-2048.crt', './certs/client-2048.pem')
        super().__init__(name, password, x_application_id)

    def __json_rpc_req(self, data: list) -> tuple:
        request_url = self.json_rpc_url  #+ '{}'.format(operation_name)
        headers = {
            'X-Application': self.x_application_id,
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-Authentication': self.session_token
        }

        exception = ''
        try:
            response = self.__s.post(url=request_url,
                                     data=json.dumps(data),
                                     headers=headers)
        except Exception as e:
            exception = str(e)
        print(response.content)
        f = open("response.json", "w+")
        f.write(str(data))
        f.close()
        return self.__res_parser(exception, response, False)

    def __rest_req(self, operation_name: str, data: dict) -> tuple:
        request_url = '{}{}/'.format(
            self.REST_url, operation_name)  #+ '{}'.format(operation_name)
        headers = {
            'X-Application': self.x_application_id,
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-Authentication': self.session_token
        }
        rb = data
        request_body = json.dumps(rb)
        exception = ''
        try:
            response = self.__s.post(url=request_url,
                                     data=request_body,
                                     headers=headers)
        except Exception as e:
            exception = str(e)
        return self.__res_parser(exception, response, False)

    def get_soccer_event_list(self) -> None:
        print('Getting soccer events list\nPOST - listEvents')
        data = {"filter": {"eventTypeIds": ["1"]}}
        try:
            self.soccer_events = []
            for event in self.__rest_req('listEvents', data)[0]:
                self.soccer_events.append(
                    self.__soccer_event_list_builder(event))
        except Exception as e:
            print('Exception {}'.format(e))
            return
        print('{} events founded'.format(len(self.soccer_events)))

    def parse_competition_req(self, output_list, temp_list, aux_index,
                              n) -> tuple:
        output_list = []
        temp_list = self.__rest_req('listCompetitions',
                                    event_ids_list[0:50])[0]
        output_list = [*output_list, *temp_list]
        aux_index += n
        sub_aux_index = n
        event_ids_list = event_ids_list[n:]
        return output_list, aux_index, sub_aux_index

    def add_n_to_competition(self, n, output_list, temp_list, aux_index,
                             event_ids_list):
        temp_list = self.__rest_req('listCompetitions',
                                    event_ids_list[0:50])[0]
        return self.parse_competition_req(self, output_list, temp_list,
                                          aux_index, 50)

    def get_competition_list(self) -> None:
        print('Getting competition list...')
        event_ids_list = [x["event_id"] for x in self.soccer_events]
        events_lenght = len(event_ids_list)
        aux_index = 0
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
        N = int(events_lenght / 100)
        N2 = events_lenght - N * 100
        for n in range(N):
            request_list.append([output_list(x) for x in event_ids_list[:100]])
            event_ids_list = event_ids_list[100:]

        if len(event_ids_list) == N2:
            request_list.append([output_list(x) for x in event_ids_list])

        for group in request_list:
            aux_response = []
            res = self.__json_rpc_req(group)[0]
            output = [*output, *res]
        #print(output)
        not_founded_ids = []
        final_output = []
        for e in output:
            if len(e['result']) != 0:
                final_output.append(
                    self.__competition_list_builder(e["result"][0], e["id"]))
            else:
                not_founded_ids.append(e["id"])
        print('final output {}'.format(final_output))
        print('not_founded list {}'.format(not_founded_ids))
        self.competition_list = final_output

        return output
