import json
from typing import List

import pandas as pd
from utils.chronos import chronometer


class DataParser:
    @staticmethod
    def __runner_to_json(runner: str) -> List[dict]:
        return json.loads(
            runner.replace("'", "~'~").replace('"', "'")
            .replace("~'~", '"')
        )

    def create_bet_columns(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        df['']
        ...
