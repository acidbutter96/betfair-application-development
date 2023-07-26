import time

from config import Logger
from utils.chronos import chronometer

from .exchange_parsers import ExchangeParsers

exchange_api_logger = Logger().get_logger("exchange_api_logger")


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
                    self.soccer_event_list_builder(event),
                )
            self.soccer_events = self.soccer_events[:1]
        except Exception as e:
            exchange_api_logger.exception(f"Exception {e}")
            return
        exchange_api_logger.info(
            f"{len(self.soccer_events)} events found")

    def get_competition_list(self, partition: int = 100) -> None:
        exchange_api_logger.info("Getting competition list...")

        self.competition_list, self.not_found_competition_ids = self.competition_partition_rpc(
            self.soccer_events, partition
        )

        exchange_api_logger.info(f"{len(self.competition_list)} competitions found\
\n{len(self.not_found_competition_ids)} competitions not found")

    def get_market_list(self, partition=100) -> None:
        exchange_api_logger.info("Getting market catalogue list...")

        self.market_catalogue_list, self.not_found_market_ids = self.market_list_partition_rpc(
            self.soccer_events, partition,
        )

        exchange_api_logger.info(
            f"Found markets from {len(self.market_catalogue_list)} events\
\n{len(self.not_found_market_ids)} not found")

    def get_market(self, partition=100) -> None:
        start = time.time()
        exchange_api_logger.info("Getting market list...")

        self.market_book_list, self.not_found_market_books = self.market_catalogue_list_partition_rpc(
            self.market_catalogue_list, partition
        )

        exchange_api_logger.info(
            f"Found markets from {len(self.market_book_list)} events\n{len(self.not_found_market_books)} not found\n\
Processed in {chronometer(start)}")

    def get_runners(self) -> None:
        start = time.time()
        exchange_api_logger.info("Getting runners list...")

        self.runners_list = self.runners_list_getter(
            self.market_catalogue_list,
        )

        exchange_api_logger.info(
            f"Found runners from {len(self.runners_list)} events\n Processed in {chronometer(start)}s",
        )
