import pandas as pd
import numpy as np
import time
from services.api import BettingAPI


class DataFrameParser(BettingAPI):

    def __init__(self):
        super().__init__('marcosp199610', 'Mmm.415263', 'IJE2hh59JFLsqo1Z')
        self.get_soccer_event_list()
        self.get_competition_list()
        self.get_market_list()

    def first_cycle(self) -> pd.DataFrame:
        df = pd.DataFrame(self.soccer_events)
        #change country code founded as numpy.nan to NF string meaning Not Founded country code
        df['event_country_code'] = df['event_country_code'].fillna(value='NF')
        #separate the home team name from away team name
        df['home_team_name'] = df['teams_name'].apply(lambda x: x[0])
        df['away_team_name'] = df['teams_name'].apply(lambda x: x[1]
                                                      if len(x) > 1 else 'N/A')
        df.insert(0, 'home_team_name', df.pop('home_team_name'))
        df.insert(1, 'away_team_name', df.pop('away_team_name'))
        #create competition_name, competition_id columns filled with TF that means To Find
        df['competition_name'] = 'TF'
        df['competition_id'] = 'TF'
        df['betname'] = 'TF'
        # betname == market name ??
        df['market_name'] = 'TF'
        df['market_id'] = 'TF'
        df['market_total_matched'] = 'TF'

        #for competition in self.competition_list:
        for i, row in df.iterrows():
            filter_competition = list(
                filter(lambda x: x["event_id"] == row['event_id'],
                       self.competition_list))
            if len(filter_competition) > 0:
                df.loc[i, 'competition_name'] = filter_competition[0][
                    'competition_name']
                df.loc[
                    i,
                    'competition_id'] = filter_competition[0]['competition_id']

        #create new rows with the market
        for e in self.market_catalogue_list:
            list_lenght = len(e['list'])
            if list_lenght > 0:
                df_it = df[df['event_id'] == e['event_id']]
                for item in e['list']:
                    df_it.loc[:, 'market_name'] = item['marketName']
                    df_it.loc[:, 'market_id'] = item['marketId']
                    df_it.loc[:, 'market_total_matched'] = item['totalMatched']
                    df = pd.concat([df_it, df], axis=0)
            else:
                df_it.loc[:, 'market_name'] = 'NF'
                df_it.loc[:, 'market_id'] = 'NF'
                df_it.loc[:, 'market_total_matched'] = 'NF'
                df = pd.concat([df_it, df], axis=0)
        df = df[df['market_name'] != 'TF']

        df = df.sort_values(['event_id', 'market_name'])

        self.df = df
        return df

    def to_csv(self):
        outputname = './output/output-{}.csv'.format(
            time.strftime("%d-%b-%Y-%H:%M:%S", time.localtime()))
        self.df.to_csv(outputname, mode='w+')
