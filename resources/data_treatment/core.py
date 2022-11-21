import asyncio
import os
import time
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from config import Logger
from services.betfair_api import ExchangeAPI
from utils.chronos import chronometer

from .builders import DataBuilder


class DataFrameParser(ExchangeAPI, DataBuilder):

    @staticmethod
    def real_odd(odd: float) -> float:
        return round(odd - 5 * (odd - 1) * 10**-2, 2)

    def __init__(self, name, password, x_application_id):
        super(ExchangeAPI, self).__init__(name, password, x_application_id)
        super(DataBuilder, self).__init__()
        self.logger = Logger().get_logger("data_frame_parser_logger")

        try:
            os.mkdir(f"{os.getcwd()}/output")
        except OSError:
            self.logger.exception(
                f"The output directory already exists or couldn't be created"
            )

    def get_data_from_api(self,) -> None:
        self.logger.info("DataFramePArser.get_data_from_api called")
        self.get_soccer_event_list()
        self.get_competition_list()
        self.get_market_list()
        self.get_runners()
        self.get_market()

    def first_cycle(self) -> float:
        self.logger.info('Data treatment\n First cycle...')
        start = time.time()
        self.df = self.create_soccer_df(
            start, self.soccer_events, self.competition_list,
        )
        # create new rows with the market
        self.logger.info("Creating market rows...\n")
        self.df = self.add_market_row(
            start, self.market_catalogue_list,
            self.df,
        )
        self.first_df_len = self.df.count()[0]
        self.logger.info(f"Total time: {chronometer(start)}")
        return start

    async def second_cycle(self) -> float:
        self.logger.info('\nEntering at the second treatment data cycle\n')
        start = time.time()

        self.df['odd'] = np.nan
        self.df['real_odd'] = np.nan
        self.df['odd_type'] = np.nan
        self.df['odd_size'] = np.nan
        self.df['bet_name'] = 'N/A'
        self.df['selection_id'] = 'TF'

        self.df_to_concat = self.df.dropna()

        async def coroutine_market_processing(mk_list: dict):
            df_to_concat = self.df_to_concat
            # list_lenght = len(mk_list)
            lil_df = self.df[:self.first_df_len]
            added_data = 0
            market_name, market_id = mk_list['market_name_id']['market_name'], mk_list['market_name_id']['market_id']
            df_it = lil_df[lil_df['market_id'] == market_id]
            splited_name = market_name.split('Over/Under')
            is_over_under = len(splited_name) >= 2

            def under_over_setence(i) -> Optional[str]:
                if is_over_under and i == 0:
                    return f"Over {splited_name[1][1:]}"
                if is_over_under and i >= 1:
                    return f"Under {splited_name[1][1:]}"
                return None

            for runner in mk_list['runners']:
                i = 0
                for back in runner['ex']['availableToBack']:
                    i += 1
                    odd = round(float(back['price']), 2)
                    size = round(float(back['size']), 2)
                    real_odd = self.real_odd(odd)
                    if is_over_under:
                        bet_name = under_over_setence(i)
                    else:
                        bet_name = market_name

                    if real_odd < odd:
                        added_data += 1
                        df_it2 = df_it[df_it['selection_id'] == 'TF']

                        df_it2.loc[:, ['selection_id', 'odd',
                                       'real_odd', 'odd_size',
                                       'odd_type', 'bet_name']] = [
                            runner['selectionId'], odd,
                            real_odd, size,
                            'back', bet_name,
                        ]
                        df_to_concat = pd.concat(
                            [df_it2, df_to_concat], axis=0)
                i = 0
                for lay in runner['ex']['availableToLay']:
                    odd = float(lay['price'])
                    size = float(lay['size'])
                    real_odd = self.real_odd(odd)
                    if is_over_under:
                        bet_name = under_over_setence(i)
                    else:
                        bet_name = market_name
                    if real_odd < odd:
                        added_data += 1
                        df_it2 = df_it[df_it['selection_id'] == 'TF']
                        df_it2.loc[:, ['selection_id', 'odd',
                                       'real_odd', 'odd_size',
                                       'odd_type', 'bet_name',
                                       ]] = [
                            runner['selectionId'], odd,
                            real_odd, size,
                            'lay', bet_name
                        ]
                        df_to_concat = pd.concat(
                            [df_to_concat, df_it2], axis=0)
                        df_to_concat = df_to_concat.sort_values(
                            ['odd_type', 'selection_id'])
            if added_data >= 1:
                self.df = pd.concat([self.df, df_to_concat], axis=0)

            print(
                f"getting runner {market_id} in {chronometer(start)}", end="\r"
            )

        tasks = []
        self.logger.info('Starting create coroutines with asyncio')
        for mk in self.market_book_list:
            tasks.append(asyncio.create_task(coroutine_market_processing(mk)))
        await asyncio.gather(*tasks)
        self.logger.info('Data processed...\nCleaning empty data')

        self.df = self.df[self.df['selection_id'] != 'TF']
        self.df.drop_duplicates(inplace=True)
        self.df.drop('market_name', axis=1, inplace=True)
        self.df.sort_values(
            ['event_id', 'selection_id', 'bet_name'], inplace=True)
        self.df.reset_index(drop=True, inplace=True)
        self.logger.info(f"Processed in {chronometer(start)}")
        return start

    def third_cycle(self) -> float:
        self.logger.info("Third cycle")
        start = time.time()

        def set_runner_name(market_id: str, selection_id: Any) -> str:
            filter_by_mk_id: List[Dict[str, Any]] = list(
                filter(
                    lambda x: x["market_id"] == market_id,
                    self.runners_list
                )
            )
            print(f"{chronometer(start)}", end="\r")
            if len(filter_by_mk_id) == 1:
                filter_by_selection_id: List[Dict[str, str]] = list(
                    filter(
                        lambda y: str(y["selection_id"]) == str(selection_id),
                        filter_by_mk_id[0]["runners"]
                    )
                )
                if len(filter_by_selection_id) == 1:
                    return filter_by_selection_id[0]["runner_name"]
                return "Not found"
            return "Not found"

        self.df['runner_name'] = self.df.apply(
            lambda row: set_runner_name(
                row["market_id"], row["selection_id"],
            ),
            axis=1,
        )

        self.logger.info(f"Total time: {chronometer(start)}")
        return start

    def to_csv(self):
        if self.df is not None:
            outputname: str = f"./output/output-{time.strftime('%d-%b-%Y-%H.%M.%S', time.localtime())}.csv"
            self.df.to_csv(outputname, mode='w+')
            self.logger.info(f"Saved as {outputname}")
        else:
            self.logger.info(
                "You must generate a data frame using api consumption or loading an existing output file - see the load_from_csv method",
            )

    def to_xlsx(self):
        if self.df is not None:
            outputname: str = f"./output/output-{time.strftime('%d-%b-%Y-%H.%M.%S', time.localtime())}.xlsx"
            self.df.to_excel(outputname)
            self.logger.info(f"Saved as {outputname}")
        else:
            self.logger.info(
                "You must generate a data frame using api consumption or loading an existing output file - see the load_from_csv method",
            )

    def load_from_csv(self, file_name: str) -> pd.DataFrame:
        file_workdir = f'./output/{file_name}'
        try:
            os.open(file_workdir, os.O_RDONLY)
            self.df = pd.read_csv(file_workdir, index_col=0)
            return self.df
        except Exception as ex:
            self.logger.exception(f"{ex}")
