from services.api import BettingAPI

betfair = BettingAPI('marcosp199610', 'Mmm.415263', 'IJE2hh59JFLsqo1Z')
data = {"filter": {"textQuery": ""}}
print(data)

teste = betfair.request_json('listEventTypes/', str(data))
