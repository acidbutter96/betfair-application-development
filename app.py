from services.api import BettingAPI

betfair = BettingAPI('marcosp199610', 'Mmm.415263', 'IJE2hh59JFLsqo1Z')
data = {"filter": {}}

#event types list
event_types_list = betfair.json_rpc_req('listEventTypes', data)
event_list = betfair.rest_req('listEvents',
                              {"filter": {
                                  "eventIds": ["31396311"]
                              }})

# event_list
competitions_list = betfair.json_rpc_req(
    'listCompetitions', {"filter": {
        "textQuery": ["31392911"]
    }})
""" f = open("competition_list.json", "x")
f.write(competitions_list[0]) """
# competition
#event_types_list = betfair.json_rpc_req('listEventTypes', data)
