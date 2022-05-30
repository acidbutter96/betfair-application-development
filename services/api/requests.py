import json

from utils.dotenv import CERTNAME

import requests

from .authentication import AuthenticationAPI


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
