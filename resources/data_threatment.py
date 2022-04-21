import pandas as pd
from services.api import BettingAPI


class DataParser(BettingAPI):

    def __init__(self):
        super().__init__('marcosp199610', 'Mmm.415263', 'IJE2hh59JFLsqo1Z')
        self.get_soccer_event_list()
        self.get_competition_list()