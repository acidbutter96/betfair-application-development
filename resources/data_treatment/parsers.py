import json
from typing import List

import pandas as pd


class DataParser:
    @staticmethod
    def __runner_to_json(runner: str) -> List[dict]:
        return json.loads(
            runner.replace("'", "~'~").replace('"', "'")
            .replace("~'~", '"')
        )

    @staticmethod
    def get_handicap_column(df: pd.DataFrame):
        handicap_parser = lambda x: x.split("~^~")[1] if "~^~" in x else 0
        runner_name_parser = lambda x: x.split("~^~")[0]
        df["handicap"] = df["runner_name"].apply(handicap_parser)
        df["runner_name"] = df["runner_name"].apply(runner_name_parser)
        return df
