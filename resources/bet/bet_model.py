from pydantic import BaseModel


class LimitOrder(BaseModel):
    size: str
    price: str
    persistence_type: str = "LAPSE"


class BetInstructions(BaseModel):
    selection_id: str
    handicap: str
    side: str
    order_type: str
    limit_order: LimitOrder


class BetBody(BaseModel):
    market_id: str
    instructions: BetInstructions
