import time

from .exchange_parsers import ExchangeParsers


class ExchangeAPI(ExchangeParsers):
    def __init__(self, name,
                 password, x_application_id
                 ):
        super().__init__(name, password, x_application_id)

    def get_soccer_event_list(self) -> None:
        print("Getting soccer events list\nPOST - listEvents")
        data = {"filter": {"eventTypeIds": ["1"]}}
        try:
            self.soccer_events = []
            for event in self.rest_req("listEvents", data)[0]:
                self.soccer_events.append(
                    self.soccer_event_list_builder(event))
        except Exception as e:
            print(f"Exception {e}")
            return
        print(f"{len(self.soccer_events)} events found")

    def get_competition_list(self, partition: int = 100) -> None:
        print("Getting competition list...")

        self.competition_list, self.not_found_competition_ids = self.competition_partition_rpc(
            self.soccer_events, partition
        )

        print(f"{len(self.competition_list)} competitions found\
            \n{len(self.not_found_competition_ids)} competitions not found")

    def get_market_list(self, partition=100) -> None:
        print("Getting market catalogue list...")

        self.market_catalogue_list, self.not_found_market_ids = self.market_list_partition_rpc(
            self.soccer_events, partition)

        print(f"Found markets from {len(self.market_catalogue_list)} events\
            \n{len(self.not_found_market_ids)} not found")

    def get_market(self, partition=100) -> None:
        start = time.time()
        print("Getting market list...")

        self.market_book_list, self.not_found_market_books = self.market_catalogue_list_partition_rpc(
            self.market_catalogue_list, partition
        )
        end = time.time()

        print(
            f"Found markets from {len(self.market_book_list)} events\n{len(self.not_found_market_books)} not found\n Processed in {round(end-start,1)}s")

    def get_runners(self) -> None:
        start = time.time()
        print("Getting runners list...")

        self.runners_list = self.runners_list_getter(
            self.market_catalogue_list,
        )
        end = time.time()

        print(
            f"Found runners from {len(self.runners_list)} events\n Processed in {round(end-start,1)}s",
        )
