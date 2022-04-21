from resources.data_threatment import DataFrameParser

betfair = DataFrameParser()
betfair.get_soccer_event_list()
betfair.get_competition_list()

#event types list
# competition
#event_types_list = betfair.json_rpc_req('listEventTypes', data)
