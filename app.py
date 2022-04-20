from services.api import BettingAPI

betfair = BettingAPI('marcosp199610', 'Mmm.415263', 'IJE2hh59JFLsqo1Z')
data = {"filter": {}}
print(data)

teste = betfair.json_rpc_req('listEventTypes', data)
