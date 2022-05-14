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
            else:
                df.loc[i, 'competition_name'] = 'N/A'
                df.loc[i, 'competition_id'] = 'N/A'

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
        df.reset_index(drop=True, inplace=True)
        end = time.time()
        total = int(end - start)
        self.df = df
        self.first_df_len = self.df.count()[0]
        print('Total time: {} seconds'.format(total))

    async def second_cycle(self)->pd.DataFrame:
        print('Entering at the second treatment data cycle')
        start = time.time()

        self.df['odd'] = np.nan
        self.df['real_odd'] = np.nan
        self.df['odd_type'] = np.nan
        self.df['odd_size'] = np.nan
        self.df['betname'] = 'N/A'
        self.df['selection_id'] = 'TF'

        self.df_to_concat = self.df.dropna()

        async def coroutine_market_processing(mk_list:list):
            df_to_concat = self.df_to_concat
            # list_lenght = len(mk_list)
            lil_df = self.df[:self.first_df_len]
            added_data=0
            df_it = lil_df[lil_df['market_id']==mk_list['market_id']]
            # print('num runners {}'.format(len(mk_list['runners'])))
            for runner in mk_list['runners']:
                # print('num av back {}'.format(len(runner['ex']['availableToBack'])))
                # print('num av lay {}'.format(len(runner['ex']['availableToLay'])))
                # print('num selection {}\n\n'.format(runner['selectionId']))
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
                        df_to_concat = pd.concat([df_to_concat,df_it2], axis=0)
                        df_to_concat = df_to_concat.sort_values(['odd_type', 'selection_id'])
            if added_data>=1:
                self.df = pd.concat([self.df,df_to_concat], axis=0)

        tasks = []
        print('Starting create coroutines with asyncio')
        for mk in self.market_book_list:
            tasks.append(asyncio.create_task(coroutine_market_processing(mk)))
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
