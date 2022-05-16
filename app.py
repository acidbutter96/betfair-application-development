import asyncio

from resources.data_treatment import DataFrameParser

betfair = DataFrameParser('marcosp199610', 'Mmm.415263', 'IJE2hh59JFLsqo1Z')
betfair.first_cycle()
asyncio.run(betfair.second_cycle())
#event types list
# competition
#event_types_list = betfair.json_rpc_req('listEventTypes', data)
