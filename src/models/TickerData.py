from typing import Optional

from pydantic import BaseModel


class TickerData(BaseModel):
    symbol: str
    high: float
    low: float
    bid: float
    bidVolume: Optional[float]
    ask: float
    askVolume: Optional[float]
    vwap: float
    open: float
    close: float
    last: float
    previousClose: Optional[float]
    change: float
    percentage: float
    average: float
    baseVolume: float
    quoteVolume: float
    last: float
    datetime: str
