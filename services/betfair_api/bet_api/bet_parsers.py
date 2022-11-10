from typing import Callable, List

from services.betfair_api.bet_api import BetBuilders, BetUtils
from services.betfair_api.betfair_parsers import BetfairApiParsers


class BetParsers(BetfairApiParsers, BetUtils, BetBuilders):

    def __init__(self, name: str,
                 password: str, x_application_id: str
                 ):
        super(BetfairApiParsers, self).__init__(
            name, password, x_application_id)
        super(BetUtils, self).__init__()
