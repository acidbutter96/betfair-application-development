from app import BetfairApplication
from resources.bet import Bet


class Example:
    betfair_application = BetfairApplication()

    def __init__(self, table_name):
        self.betfair_application.load_from_csv(
            file_name=table_name,
        )

    def bet_from_table(self,):
        df = self.betfair_application.df[:100]

        self.bet = Bet(
            data_frame=df, handicap='handicap',
            order_type='order_type', persistence_type='persistence_type',
            price='10', side='LAY',
            size='3',
        )

    def test_save_in_xlsx(self,):
        self.betfair_application.data_frame_parser.to_xlsx()


bet_example = Example('output-03-Aug-2022-02.54.28.csv')
bet_example.bet_from_table()
bet_list = bet_example.bet.create_bets_list(
    handicap='handicap', price='10',
    side='side', size='size',
)
print(bet_list)
