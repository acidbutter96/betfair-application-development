import json
import betfairlightweight


class BetFairAPI:
    betfair_url = 'https://api.betfair.com/v1/account'

    def __init__(self, name: str, password: str,
                 x_application_id: str) -> None:
        self.trading = betfairlightweight.APIClient(
            username=name,
            password=password,
            app_key=x_application_id,
            certs='certs/client-2048.crt')
