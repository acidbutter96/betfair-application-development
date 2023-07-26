from pydantic import BaseModel


class LimitOrder(BaseModel):
    size: str
    price: str
    persistenceType: str = "LAPSE"


class BetInstructions(BaseModel):
    selectionId: str
    handicap: str
    side: str
    orderType: str
    limitOrder: LimitOrder


class BetBody(BaseModel):
    id: str
    marketId: str
    instructions: BetInstructions
