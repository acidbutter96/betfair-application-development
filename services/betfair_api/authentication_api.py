from services.betfair_api.connector import Connector


class AuthenticationAPI(Connector):
    def __init__(self, name: str,
        password: str, x_application_id: str
    ) -> None:
        self.auth_name= name

        super().__init__()

        url = "https://identitysso-cert.betfair.com/api/certlogin"
        headers = {
            "X-Application": x_application_id,
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {"username": name, "password": password}

        r = self._session.post(url=url, data=data, headers=headers)
        self.__auth = r.json()
        if self.__auth["loginStatus"] == "SUCCESS":
            self.auth_headers = {
                "X-Application": x_application_id,
                "Accept": "application/json",
                "Content-Type": "application/json",
                "X-Authentication": self.__auth["sessionToken"]
                }
            print(f"User: {data['username']} is authenticated")
            return None
        if self.__auth["loginStatus"] == "SUSPENDED":
            raise Exception(f'API Error: {self.__auth["loginStatus"]}')
        raise Exception("Authentication failed, verify your credentials and\
                    try again")
