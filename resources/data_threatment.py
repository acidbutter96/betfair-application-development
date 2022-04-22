import pandas as pd
from services.api import BettingAPI


class DataFrameParser(BettingAPI):

    def __init__(self):
        super().__init__('marcosp199610', 'Mmm.415263', 'IJE2hh59JFLsqo1Z')
        self.get_soccer_event_list()
        self.get_competition_list()

    def first_cycle(self) -> pd.DataFrame:
        concatenated = []
        for event in self.soccer_events:
            concatenated.append(self.get_competition(event["event_id"]))
        self.competition_list = concatenated
        self.df = pd.concat([
            pd.DataFrame(self.soccer_events),
            pd.DataFrame(self.competition_list)
        ])

        return self.df
