import pandas as pd
from services.api import BettingAPI


class DataFrameParser(BettingAPI):

    def __init__(self):
        super().__init__('marcosp199610', 'Mmm.415263', 'IJE2hh59JFLsqo1Z')
        self.get_soccer_event_list()
        self.get_competition_list()

    def first_cycle(self) -> pd.DataFrame:
        soccer_df = pd.DataFrame(self.soccer_events)
        print(self.soccer_events)

        return soccer_df