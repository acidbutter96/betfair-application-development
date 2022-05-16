import asyncio
import os

from dotenv import load_dotenv

from resources.data_treatment import DataFrameParser

load_dotenv()

x_application_id = os.getenv('X_APPLICATION_ID')
name = os.getenv('NAME')
password = os.getenv('PASSWORD')
print(f"name {name} password {password} x_app {x_application_id}")
betfair = DataFrameParser(name, password, x_application_id)
betfair.first_cycle()
asyncio.run(betfair.second_cycle())
#event types list
# competition
#event_types_list = betfair.json_rpc_req('listEventTypes', data)
