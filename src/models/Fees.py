from typing import Optional

from pydantic import BaseModel


class Fees(BaseModel):
    symbol: Optional[str]
    taker_fee_percent: float
    maker_fee_percent: float
    exchange_name: str
