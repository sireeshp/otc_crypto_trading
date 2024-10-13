from dataclasses import dataclass
from src.models.BestPriceData import BestPriceData
from typing import List
from src.models.OrderBookData import OrderBookData

@dataclass
class PriceEngineData:
    best_bid: BestPriceData
    best_ask:BestPriceData
    exchange_data:List[OrderBookData]