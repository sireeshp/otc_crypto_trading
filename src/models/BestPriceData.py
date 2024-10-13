from dataclasses import dataclass
from typing import Tuple
@dataclass
class BestPriceData:
    price: Tuple[float, float]  # (price, volume)
    exchange: str