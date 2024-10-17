from typing import List, Optional

from pydantic import BaseModel

from src.models.BestPriceModel import BestPriceData
from src.models.OrderBookDataModel import OrderBookData


class PriceEngineData(BaseModel):
    best_bid: BestPriceData
    best_ask: BestPriceData
    exchange_data: Optional[List[OrderBookData]]
