import pandas as pd
from services.api import BettingAPI


class DataFrameParser(BettingAPI):

    def __init__(self):
        super().__init__('marcosp199610', 'Mmm.415263', 'IJE2hh59JFLsqo1Z')
        self.get_soccer_event_list()
        self.get_competition_list()

    def first_cycle(self) -> pd.DataFrame:
        df = pd
        """ 
            soccer event data structure
            {
                'event': {
                    'id': '31397413',
                    'name': 'Genclerbirligi v Bandirmaspor',
                    'countryCode': 'TR',
                    'timezone': 'GMT',
                    'openDate': '2022-04-23T13:00:00.000Z'},
                    'marketCount': 24
                }
            }
            competition list data structure
            {
                'competition': {
                'id': '12220485',
                'name': "FIFA Women's World Cup"
                },
            'marketCount': 1,
            'competitionRegion': 'International'
            }
            refactor
            soccer
            {
                "id": "31397413",
                "name": "Genclerbirligi v Bandirmaspor",
                "countryCode": "TR",
                "timezone": "GMT",
                "openDate": "2022-04-23T13:00:00.000Z"},
                "marketCount": 24,
            }
            competition
            {
                'id': '12220485',
                'name': "FIFA Women's World Cup"
                'marketCount': 1,
                'competitionRegion': 'International'
            }
         """
        pass