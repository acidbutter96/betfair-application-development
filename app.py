from resources.data_threatment import DataParser

betfair = DataParser()
betfair.get_soccer_event_list()
print(betfair.soccer_events)
betfair.get_competition_list()
print(betfair.competition_list)

#event types list
""" event_types_list = betfair.json_rpc_req('listEventTypes', data)
event_list = betfair.rest_req('listEvents',
                              {"filter": {
                                  "eventIds": ["31396311"]
                              }}) """

# event_list
""" competitions_list = betfair.json_rpc_req(
    'listCompetitions', {"filter": {
        "textQuery": ["31392911"]
    }}) """
""" f = open("competition_list.json", "x")
f.write(competitions_list[0]) """
# competition
#event_types_list = betfair.json_rpc_req('listEventTypes', data)
