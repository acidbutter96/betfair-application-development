from typing import Any, Dict, List

from config import config
from resources.bet.bet_model import BetBody
from services.betfair_api.exchange_api import ExchangeAPI


class BetAPI(ExchangeAPI):
    @staticmethod
    def __bet_list_builder(event: BetBody) -> Dict:
        data: Dict[str, str | Any] = {
            "jsonrpc": "2.0",
            "method": "SportsAPING/v1.0/placeOrders",
        }
        data['instruction'] = event.dict()

        del data['instruction']['id']

        data['id'] = event.id

        return data

    def __init__(
        self, name,
        password, x_application_id
    ):
        self.__s.cert = (f"./certs/{config.CERTNAME}.crt",
                         f"./certs/{config.CERTNAME}.pem")
        super().__init__(name, password, x_application_id)

    def bet_on(self, bet_list: List[BetBody]):
        data = [self.__bet_list_builder(x) for x in bet_list]
        request = super().json_rpc_req(data)
        ...
