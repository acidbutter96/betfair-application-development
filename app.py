import asyncio

from resources.data_treatment import DataFrameParser
from utils.dotenv import NAME, PASSWORD, X_APPLICATION_ID

betfair = DataFrameParser(NAME, PASSWORD, X_APPLICATION_ID)
betfair.first_cycle()
# asyncio.run(betfair.second_cycle())
# betfair.third_cycle()
# event types list
# competition
#event_types_list = betfair.json_rpc_req('listEventTypes', data)
