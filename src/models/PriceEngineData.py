from typing import List, Optional

from pydantic import BaseModel

from src.models.BestPriceData import BestPriceData
from src.models.OrderBookData import OrderBookData


class PriceEngineData(BaseModel):
    best_bid: BestPriceData
    best_ask: BestPriceData
    exchange_data: Optional[List[OrderBookData]]
