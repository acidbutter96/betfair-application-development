import pandas as pd
import numpy as np
from services.api import BettingAPI


class DataFrameParser(BettingAPI):

    def __init__(self):
        super().__init__('marcosp199610', 'Mmm.415263', 'IJE2hh59JFLsqo1Z')
        self.get_soccer_event_list()
        self.get_competition_list()

    def first_cycle(self) -> pd.DataFrame:
        self.df = pd.DataFrame(self.soccer_events)
        #change country code founded as numpy.nan to NF string meaning Not Founded country code
        self.df['event_country_code'] = self.df['event_country_code'].fillna(
            value='NF')
        #create competition_name, competition_id columns filled with TF that means To Find
        self.df['competition_name'] = 'TF'
        self.df['competition_id'] = 'TF'
        #make N blocks of 100 different countries
        countries_groups = []
        country_founded = self.df[self.df['event_country_code'] != 'NF'][[
            'event_country_code', 'event_id'
        ]]

        return
