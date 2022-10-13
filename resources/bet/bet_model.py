class LimitOrder:
    size: str
    price: str
    persistence_type: str = "LAPSE"


class BetInstructions:
    selection_id: str
    handicap: str
    side: str
    order_type: str
    limit_order: LimitOrder


class BetBody:
    market_id: str
    instructions: BetInstructions
