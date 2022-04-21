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

    def __init__(self, name, password, x_application_id):
        self.__s.cert = ('./certs/client-2048.crt', './certs/client-2048.pem')
        super().__init__(name, password, x_application_id)

    def json_rpc_req(self, operation_name: str, data) -> tuple:
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

    def rest_req(self, operation_name: str, data: dict) -> tuple:
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
