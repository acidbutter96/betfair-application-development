from app import BetfairApplication

betfair_application = BetfairApplication()
betfair_application.load_from_api()
betfair_application.save_excel()
