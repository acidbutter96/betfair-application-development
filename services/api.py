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
    def __res_parser(exception, response, error_key, rest=False):
        if exception != '':
            raise Exception(exception)
            return
        if error_key or response.status_code != 200:
            raise Exception(
                "Bad request\n response code: {}\n Body response: {}".format(
                    response.status_code, response.content, exception))
        if not rest:
            return response.json()['result'], response.json(
            ), response.status_code, response.url
        return response.json(), response.json(
        ), response.status_code, response.url

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
    def __competition_list_builder(competition) -> dict:
        comp_keys = list(competition.keys())
        has_comp = comp_keys.count("competition") == 1
        has_mkt_count = comp_keys.count("marketCount") == 1
        has_comp_reg = comp_keys.count("competitionRegion") == 1

        data = {}

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

    def __json_rpc_req(self, operation_name: str, data) -> tuple:
        request_url = self.json_rpc_url  #+ '{}'.format(operation_name)
        headers = {
            'X-Application': self.x_application_id,
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-Authentication': self.session_token
        }
        rb = {
            "jsonrpc": "2.0",
            "method": "SportsAPING/v1.0/{}".format(operation_name),
            "params": [data],
            "id": 1
        }
        request_body = json.dumps(rb)
        exception = ''
        try:
            response = self.__s.post(url=request_url,
                                     data=request_body,
                                     headers=headers)
        except Exception as e:
            exception = str(e)
        error_key = list(response.json().keys()).count('error') == 1
        return self.__res_parser(exception, response, error_key)

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
        return self.__res_parser(exception, response, False, True)

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
        event_ids_list = [x["event_id"] for x in self.soccer_events]
        events_lenght = len(event_ids_list)
        aux_index = 0
        output_list = []
        all_competitions = self.get_competitions(event_ids_list)

        while aux_index < events_lenght:
            remainscent_index = events_lenght - aux_index

            print(
                'events lenght: {}\naux index: {}\nremainscent index: {}\n\n'.
                format(events_lenght, aux_index, remainscent_index))

            if len(all_competitions) == events_lenght:
                aux_index = events_lenght
                output_list = all_competitions
                break
            else:
                first_100 = self.get_competitions(event_ids_list[:100])
                print('First 100 {}\n'.format(len(first_100)))
                if len(first_100) == 100 and not remainscent_index < 100:
                    #print('Has 100 competitions\n{} event length'.format(aux_index))
                    output_list = [*output_list, first_100]
                    event_ids_list = event_ids_list[100:]
                    aux_index = aux_index + 100
                else:
                    first_50 = self.get_competitions(event_ids_list[:50])
                    print('First 50 {}\n'.format(len(first_50)))
                    if len(first_50) == 50 and not remainscent_index < 50:
                        output_list = [*output_list, *first_50]
                        event_ids_list = event_ids_list[50:]
                        aux_index = aux_index + 50
                    else:
                        first_25 = self.get_competitions(event_ids_list[:25])
                        print('First 25 {}\n'.format(len(first_25)))
                        if len(first_25) == 25 and not remainscent_index < 25:
                            output_list = [*output_list, *first_25]
                            event_ids_list = event_ids_list[25:]
                            aux_index = aux_index + 25
                        else:
                            first_10 = self.get_competitions(
                                event_ids_list[:10])
                            print('First 10 {}\n'.format(len(first_10)))
                            if len(first_10
                                   ) == 10 and not remainscent_index < 10:
                                output_list = [*output_list, *first_10]
                                event_ids_list = event_ids_list[10:]
                                aux_index = aux_index + 10
                            else:
                                first = self.get_competitions(
                                    event_ids_list[0])
                                print('First {}\n'.format(first))
                                if len(first) == 1:
                                    output_list = [*output_list, first]
                                    event_ids_list = event_ids_list[1:]
                                    aux_index = aux_index + 1
                                else:
                                    output_list = [
                                        *output_list, {
                                            "competition_id": "0",
                                            "competition_name": "Unknown",
                                            "competition_market_count":
                                            "Unknown",
                                            "competition_region": "Unknown"
                                        }
                                    ]
                                    output_list = [*output_list, first]
                                    event_ids_list = event_ids_list[1:]
                                    aux_index += 1
                print(len(event_ids_list))
                print(output_list)
                #print('end of loop')
                if aux_index == events_lenght:
                    print('has ended')
                    break
        print(output_list)
        return output_list

    def get_competitions(self, list: list) -> list:
        data = {"filter": {"eventIds": [*list]}}
        competition_list = []
        try:
            #print('Getting data...')
            for comp in self.__rest_req('listCompetitions', data)[0]:
                competition_list.append(self.__competition_list_builder(comp))
        except Exception as e:
            print('Exception {}'.format(e))
            return
        #print('{} events founded'.format(len(competition_list)))
        return competition_list
