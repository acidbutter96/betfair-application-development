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
    url = 'https://api.betfair.com/exchange/betting/rest/v1.0/'

    def __init__(self, name, password, x_application_id):
        self.__s.cert = ('./certs/client-2048.crt', './certs/client-2048.pem')
        super().__init__(name, password, x_application_id)

    def request_json(self, operation_name: str, data):
        request_url = self.url + '{}'.format(operation_name)
        headers = {
            'X-Application': self.x_application_id,
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-Authentication': self.session_token
        }

        response = self.__s.post(url=request_url, data=data, headers=headers)
        return response
