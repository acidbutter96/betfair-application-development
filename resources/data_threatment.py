import asyncio
import time

import numpy as np
import pandas as pd
from services.api import BettingAPI


class DataFrameParser(BettingAPI):

    @staticmethod
    def real_odd(odd:float)->float:
        return round(odd-5*(odd-1)*10**-2,2)

    def __init__(self):
        super().__init__('marcosp199610', 'Mmm.415263', 'IJE2hh59JFLsqo1Z')
        self.get_soccer_event_list()
        self.get_competition_list()
        self.get_market_list()
        self.get_market()

    async def coroutine_markets(self,e):
        list_lenght = len(e['list'])
        if list_lenght > 0:
            df_it = self.df[self.df['event_id'] == e['event_id']]
            for item in e['list']:
                df_it.loc[:, 'market_name'] = item['marketName']
                df_it.loc[:, 'market_id'] = item['marketId']
                df_it.loc[:, 'market_total_matched'] = item['totalMatched']
                self.df = pd.concat([df_it, self.df], axis=0)
        else:
            df_it.loc[:, 'market_name'] = 'NF'
            df_it.loc[:, 'market_id'] = 'NF'
            df_it.loc[:, 'market_total_matched'] = 'NF'
            self.df = pd.concat([df_it, self.df], axis=0)

    async def first_cycle(self) -> None:
        print('Data treatment\n First cycle...')
        start = time.time()
        self.df = pd.DataFrame(self.soccer_events)
        #change country code founded as numpy.nan to NF string meaning Not Founded country code
        self.df['event_country_code'] = self.df['event_country_code'].fillna(value='NF')
        #separate the home team name from away team name
        self.df['home_team_name'] = self.df['teams_name'].apply(lambda x: x[0])
        self.df['away_team_name'] = self.df['teams_name'].apply(lambda x: x[1]
                                                      if len(x) > 1 else 'N/A')
        self.df.insert(0, 'home_team_name', self.df.pop('home_team_name'))
        self.df.insert(1, 'away_team_name', self.df.pop('away_team_name'))
        self.df.insert(0, 'event_id', self.df.pop('event_id'))
        self.df.drop('teams_name', axis=1, inplace=True)
        #create competition_name, competition_id columns filled with TF that means To Find
        self.df['competition_name'] = 'TF'
        self.df['competition_id'] = 'TF'
        # self.df['betname'] = 'TF'
        # betname == market name ??
        self.df['market_name'] = 'TF'
        self.df['market_id'] = 'TF'
        self.df['market_total_matched'] = 'TF'

        #for competition in self.competition_list:
        for i, row in self.df.iterrows():
            filter_competition = list(
                filter(lambda x: x["event_id"] == row['event_id'],
                       self.competition_list))
            if len(filter_competition) > 0:
                df.loc[i, 'competition_name'] = filter_competition[0][
                    'competition_name']
                df.loc[
                    i,
                    'competition_id'] = filter_competition[0]['competition_id']
            else:
                df.loc[i, 'competition_name'] = 'N/A'
                df.loc[i, 'competition_id'] = 'N/A'

        #create new rows with the market
        tasks = []
        for e in self.market_catalogue_list:
            #async
            tasks.append(asyncio.create_task(self.coroutine_markets(e)))
        await asyncio.gather(*tasks)
        self.df = self.df[self.df['market_name'] != 'TF']

        self.df = self.df.sort_values(['event_id', 'market_name'])
        self.df.reset_index(drop=True, inplace=True)
        end = time.time()
        total = int(end - start)
        print('Total time: {} seconds'.format(total))

    async def coroutine_market_processing(self,mk_list:list):
        df_to_concat = self.df.dropna()
        list_lenght = len(mk_list)
        lil_df = self.df
        added_data=0
        if list_lenght > 0:
            df_it = lil_df[lil_df['market_id']==mk_list[0]['marketId']]
            for runner in mk_list[0]['runners']:
                for back in runner['ex']['availableToBack']:
                    odd = round(float(back['price']),2)
                    size = round(float(back['size']),2)
                    real_odd = self.real_odd(odd)
                    if real_odd < odd:
                        added_data+=1
                        df_it2 = df_it[df_it['selection_id']=='TF']
                        df_it2.loc[:,['selection_id','odd','real_odd','odd_size','odd_type']]=[runner['selectionId'],
                                                    odd,real_odd,size,'back']
                    df_to_concat = pd.concat([df_it2, df_to_concat], axis=0)
                
                for lay in runner['ex']['availableToLay']:
                    odd = float(lay['price'])
                    size = float(lay['size'])
                    real_odd = self.real_odd(odd)
                    if real_odd < odd:
                        added_data+=1
                        df_it2 = df_it[df_it['selection_id']=='TF']
                        df_it2.loc[:,['selection_id', 'odd', 'real_odd','odd_size', 'odd_type']] = [runner['selectionId'],
                                                        odd, real_odd, size,'lay']
                    df_to_concat = pd.concat([df_it2, df_to_concat], axis=0)
        if added_data>=1:
            self.df = pd.concat([df_to_concat, self.df], axis=0)

    async def second_cycle(self)->pd.DataFrame:
        print('Entering at the second treatment data cycle')
        start = time.time()

        self.df['odd'] = np.nan
        self.df['real_odd'] = np.nan
        self.df['odd_type'] = np.nan
        self.df['odd_size'] = np.nan
        self.df['selection_id'] = 'TF'

        tasks = []
        print('Starting create coroutines with asyncio')
        for mk in self.market_book_list:
            mk_list = mk['list']
            tasks.append(asyncio.create_task(self.coroutine_market_processing(mk_list)))
        await asyncio.gather(*tasks)
        print('Data processed...\nCleaning empty data')

        self.df = self.df[self.df['selection_id'] != 'TF']
        end = time.time()
        print('Processed in {}'.format(end-start))
        return None

    def to_csv(self):
        outputname = './output/output-{}.csv'.format(
            time.strftime("%d-%b-%Y-%H.%M.%S", time.localtime()))
        self.df.to_csv(outputname, mode='w+')
