import pandas as pd
from pandas import DataFrame

from config import Logger
from utils.chronos import chronometer

from .parsers import DataParser

data_builder_logger = Logger().get_logger("data_builder_logger")


class DataBuilder(DataParser):
    def __init__(self):
        super().__init__()

    def create_soccer_df(
        self, start: float,
        soccer_events: list, competition_list: list,
    ) -> DataFrame:
        df = pd.DataFrame(soccer_events)
        # change country code found as numpy.nan to NF string meaning Not found country code
        df['event_country_code'] = df['event_country_code'].fillna(value='NF')
        # separate the home team name from away team name
        df['home_team_name'] = df['teams_name'].apply(lambda x: x[0])
        self.teams_name = df['teams_name']
        self.away_team_name = df['teams_name'].apply(
            lambda x: x[1] if len(x) > 1 else 'N/A'
        )
        df['away_team_name'] = df['teams_name'].apply(
            lambda x: x[1] if len(x) > 1 else 'N/A'
        )
        df.insert(0, 'home_team_name', df.pop('home_team_name'))
        df.insert(1, 'away_team_name', df.pop('away_team_name'))
        df.insert(0, 'event_id', df.pop('event_id'))
        df.drop('teams_name', axis=1, inplace=True)
        # create competition_name, competition_id columns filled with TF that means To Find
        df['competition_name'] = 'TF'
        df['competition_id'] = 'TF'
        # betname == market name ??
        df['market_name'] = 'TF'
        df['runners'] = 'TF'
        df['market_id'] = 'TF'
        df['market_total_matched'] = 'TF'

        # for competition in self.competition_list:
        for i, row in df.iterrows():
            filter_competition = list(
                filter(lambda x: x["event_id"] == row['event_id'],
                       competition_list)
            )
            if len(filter_competition) > 0:
                df.loc[i, 'competition_name'] = filter_competition[0]['competition_name']
                df.loc[
                    i,
                    'competition_id',
                ] = str(filter_competition[0]['competition_id'])
            else:
                df.loc[i, 'competition_name'] = 'N/A'
                df.loc[i, 'competition_id'] = 'N/A'
            print(f"Processing from {i} in {chronometer(start)}", end="\r")
        data_builder_logger.info(f"Processed in {chronometer(start)}")

        return df

    def add_market_row(self, start: float, market_catalogue_list: list, df: DataFrame) -> DataFrame:
        for e in market_catalogue_list:
            list_lenght = len(e['list'])
            if list_lenght > 0:
                df_it = df[df['event_id'] == e['event_id']]
                for item in e['list']:
                    # print(str(item['runners']))
                    df_it.loc[:, 'market_name'] = item['marketName']
                    df_it.loc[:, 'market_id'] = item['marketId']
                    df_it.loc[:, 'market_total_matched'] = item['totalMatched']
                    df_it.loc[:, 'runners'] = str(item['runners'])
                    df = pd.concat([df_it, df], axis=0)
            else:
                df_it.loc[:, 'market_name'] = 'NF'
                df_it.loc[:, 'market_id'] = 'NF'
                df_it.loc[:, 'market_total_matched'] = 'NF'
                df_it.loc[:, 'runners'] = 'NF'
                df = pd.concat([df_it, df], axis=0)
            print(
                f"Processing from {e['event_id']} in {chronometer(start)}",
                end="\r",
            )
        data_builder_logger.info(f"Processed in {chronometer(start)}")
        df = df[df['market_name'] != 'TF']

        df = df.sort_values(['event_id', 'market_name'])
        df.reset_index(drop=True, inplace=True)

        return df
