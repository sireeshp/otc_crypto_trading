from dataclasses import dataclass
from typing import List, Tuple, Union

@dataclass
class TickerData:
    symbol:str
    high:float
    low:float
    bid:float
    bidVolume:Union[float,None]
    ask:float
    askVolume:Union[float,None]
    vwap:float
    open:float
    close:float
    last:float
    previousClose:Union[float,None]
    change:float
    percentage:float
    average:float
    baseVolume:float
    quoteVolume:float
    last:float
    datetime:str