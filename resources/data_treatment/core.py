import asyncio
import os
import time

import numpy as np
import pandas as pd
from services.betfair_api import ExchangeAPI
from utils.chronos import chronometer

from .parsers import DataParser


class DataFrameParser(ExchangeAPI, DataParser):

    @staticmethod
    def real_odd(odd:float)->float:
        return round(odd-5*(odd-1)*10**-2,2)

    def __init__(self, name, password, x_application_id):
        super().__init__(name, password, x_application_id)

        try:
            os.mkdir(f"{os.getcwd()}/output")
        except OSError:
            print(f"The output directory already exists or couldn't be created")

        self.get_soccer_event_list()
        self.get_competition_list()
        self.get_market_list()
        self.get_market()

    def first_cycle(self) -> None:
        print('Data treatment\n First cycle...')
        start = time.time()
        df = pd.DataFrame(self.soccer_events)
        #change country code founded as numpy.nan to NF string meaning Not Founded country code
        df['event_country_code'] = df['event_country_code'].fillna(value='NF')
        #separate the home team name from away team name
        df['home_team_name'] = df['teams_name'].apply(lambda x: x[0])
        df['away_team_name'] = df['teams_name'].apply(lambda x: x[1]
                                                      if len(x) > 1 else 'N/A')
        df.insert(0, 'home_team_name', df.pop('home_team_name'))
        df.insert(1, 'away_team_name', df.pop('away_team_name'))
        df.insert(0, 'event_id', df.pop('event_id'))
        df.drop('teams_name', axis=1, inplace=True)
        #create competition_name, competition_id columns filled with TF that means To Find
        df['competition_name'] = 'TF'
        df['competition_id'] = 'TF'
        # betname == market name ??
        df['market_name'] = 'TF'
        df['runners'] = 'TF'
        df['market_id'] = 'TF'
        df['market_total_matched'] = 'TF'

        #for competition in self.competition_list:
        for i, row in df.iterrows():
            filter_competition = list(
                filter(lambda x: x["event_id"] == row['event_id'],
                       self.competition_list)
                )
            if len(filter_competition) > 0:
                df.loc[i, 'competition_name'] = filter_competition[0][
                    'competition_name']
                df.loc[
                    i,
                    'competition_id'] = filter_competition[0]['competition_id']
            else:
                df.loc[i, 'competition_name'] = 'N/A'
                df.loc[i, 'competition_id'] = 'N/A'
            print(f"Processing from {i} in {chronometer(start)}", end="\r")
        print(f"Processed in {chronometer(start)}\n")

        #create new rows with the market
        print("Creating market rows...\n")
        for e in self.market_catalogue_list:
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
            print(f"Processing from {e['event_id']} in {chronometer(start)}", end="\r")
        print(f"\nProcessed in {chronometer(start)}\n")
        df = df[df['market_name'] != 'TF']

        df = df.sort_values(['event_id', 'market_name'])
        df.reset_index(drop=True, inplace=True)
        self.df = df
        self.first_df_len = self.df.count()[0]
        print(f"Total time: {chronometer(start)}")

    def market_cycle(self):
        self.df = self.create_bet_columns(self.df)
        
        ...

    async def second_cycle(self)->pd.DataFrame:
        print('\nEntering at the second treatment data cycle\n')
        start = time.time()

        self.df['odd'] = np.nan
        self.df['real_odd'] = np.nan
        self.df['odd_type'] = np.nan
        self.df['odd_size'] = np.nan
        self.df['bet_name'] = 'N/A'
        self.df['selection_id'] = 'TF'

        self.df_to_concat = self.df.dropna()

        async def coroutine_market_processing(mk_list:list):
            df_to_concat = self.df_to_concat
            # list_lenght = len(mk_list)
            lil_df = self.df[:self.first_df_len]
            added_data=0
            [market_name,market_id] = mk_list['market_name_id'].split('_~_')
            df_it = lil_df[lil_df['market_id']==market_id]
            splited_name = market_name.split('Over/Under')
            is_over_under = len(splited_name)>=2

            def under_over_setence(i)->str:
                if is_over_under and i==0:
                    return f"Over {splited_name[1][1:]}"
                if is_over_under and i>=1:
                    return f"Under {splited_name[1][1:]}"

            for runner in mk_list['runners']:
                i=0
                for back in runner['ex']['availableToBack']:
                    i+=1
                    odd = round(float(back['price']),2)
                    size = round(float(back['size']),2)
                    real_odd = self.real_odd(odd)
                    if is_over_under:
                        bet_name = under_over_setence(i)
                    else:
                        bet_name = market_name
                    if real_odd < odd:
                        added_data+=1
                        df_it2 = df_it[df_it['selection_id'] == 'TF']
                        
                        df_it2.loc[:,['selection_id','odd',
                                        'real_odd','odd_size',
                                        'odd_type','bet_name']] = [
                                            runner['selectionId'],odd,
                                            real_odd,size,
                                            'back',bet_name]
                        df_to_concat = pd.concat([df_it2, df_to_concat], axis=0)
                i=0
                for lay in runner['ex']['availableToLay']:
                    odd = float(lay['price'])
                    size = float(lay['size'])
                    real_odd = self.real_odd(odd)
                    if is_over_under:
                        bet_name = under_over_setence(i)
                    else:
                        bet_name = market_name
                    if real_odd < odd:
                        added_data+=1
                        df_it2 = df_it[df_it['selection_id']=='TF']
                        df_it2.loc[:,['selection_id', 'odd',
                                        'real_odd','odd_size',
                                        'odd_type','bet_name']] = [
                                            runner['selectionId'],odd,
                                            real_odd, size,
                                            'lay',bet_name]
                        df_to_concat = pd.concat([df_to_concat,df_it2], axis=0)
                        df_to_concat = df_to_concat.sort_values(['odd_type', 'selection_id'])
            if added_data>=1:
                self.df = pd.concat([self.df,df_to_concat], axis=0)
            
            print(f"getting runner {market_id} in {chronometer(start)}",end="\r")

        tasks = []
        print('Starting create coroutines with asyncio')
        for mk in self.market_book_list:
            tasks.append(asyncio.create_task(coroutine_market_processing(mk)))
        await asyncio.gather(*tasks)
        print('Data processed...\nCleaning empty data')

        self.df = self.df[self.df['selection_id'] != 'TF']
        self.df.drop_duplicates(inplace=True)
        self.df.drop('market_name', axis=1, inplace=True)
        self.df.sort_values(['event_id', 'selection_id','bet_name'],inplace=True)
        self.df.reset_index(drop=True, inplace=True)

        end = time.time()
        print(f"Processed in {chronometer(end-start)}")
        self.to_csv()
        print(f"Saved as {self.outputname}")

    def to_csv(self):
        self.outputname:str = f"./output/output-{time.strftime('%d-%b-%Y-%H.%M.%S', time.localtime())}.csv"
        self.df.to_csv(self.outputname, mode='w+')
