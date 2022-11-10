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
