import json
from typing import List

import pandas as pd


class DataParser:
    def __runner_to_json(runner:str)->List[dict]:
        return json.loads(
            runner.replace("'","~'~").replace('"',"'")
            .replace("~'~",'"')
        )

    def create_bet_columns(self, df:pd.DataFrame, **kwargs)->pd.DataFrame:
        df['']
        ...
