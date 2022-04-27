import pandas as pd
import numpy as np
import time
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

        for competition in self.competition_list:
            for i, row in self.df.iterrows():
                if row['event_id'] == competition['event_id']:
                    self.df.loc[
                        i,
                        'competition_name'] = competition['competition_name']
                    self.df.loc[
                        i, 'competition_id'] = competition['competition_id']

        return self.df

    def to_csv(self):
        outputname = './output/output-{}.csv'.format(
            time.strftime("%d-%b-%Y-%H:%M:%S", time.localtime()))
        self.df.to_csv(outputname, mode='w+')
