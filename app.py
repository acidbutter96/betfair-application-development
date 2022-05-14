import asyncio

from resources.data_threatment import DataFrameParser

betfair = DataFrameParser()
asyncio.run(betfair.first_cycle())
asyncio.run(betfair.second_cycle())
#event types list
# competition
#event_types_list = betfair.json_rpc_req('listEventTypes', data)
