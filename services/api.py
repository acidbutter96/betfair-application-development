import requests
import json


class BetFairAPI:
    betfair_url = 'https://api.betfair.com/v1/account'
    s = requests.Session()

    def __init__(self, name: str, password: str,
                 x_application_id: str) -> None:
        self.auth_name = name
        self.x_application_id = x_application_id
        """ s = requests.Session()
        s.verify = 'certificates/ssl_cert' """
        url = 'https://identitysso.betfair.com/api/login/'
        auth_url = url
        headers = {
            'X-Application': x_application_id,
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {'name': name, 'password': password}
        data = json.dumps(data)
        print(data)
        self.r = self.s.post(url=auth_url,
                             data=data,
                             headers=headers,
                             cert=('/certs/client-2048.crt',
                                   '/certs/client-2048.key'))
        self.data = self.r
        print(self.r.json())

    def to_json(self):
        return self.data
