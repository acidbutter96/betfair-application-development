import json

from services.betfair_api.authentication_api import AuthenticationAPI


class RequestAPI(AuthenticationAPI):
    
    def __init__(self, name,
        password, x_application_id
    ):
        super(AuthenticationAPI, self).__init__(name, password,
            x_application_id
        )

    @staticmethod
    def __res_parser(exception, response,
        error_key
    ):
        if exception != "":
            raise Exception(exception)
        if error_key or response.status_code != 200:
            raise Exception(
                f"Bad request: {exception}\n response code: {response.status_code}\n\
                    Body response: {response.content}"
            )
        return response.json(), response.status_code, response.url

    def json_rpc_req(self, data: list) -> tuple:
        request_url = self.json_rpc_url  #+ '{}'.format(operation_name)
        exception = ""
        try:
            response = self._session.post(url=request_url, data=json.dumps(data),
                headers=self.auth_headers
            )
        except Exception as e:
            exception = str(e)
        return self.__res_parser(exception, response, False)

    def rest_req(self, operation_name: str,
        data: dict
    ) -> tuple:
        request_url = f"{self.REST_url}{operation_name}/" #+ '{}'.format(operation_name)
        rb = data
        request_body = json.dumps(rb)
        exception = ""
        try:
            response = self._session.post(url=request_url, data=request_body,
                headers=self.auth_headers
            )
        except Exception as e:
            exception = str(e)
        return self.__res_parser(exception, response, False)
