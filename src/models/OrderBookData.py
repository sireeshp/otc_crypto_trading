from pydantic import BaseModel
from dataclasses import dataclass
from typing import Tuple,List,Union

@dataclass
class OrderBookData(BaseModel):
    top_bid:Tuple[float,float] # (price,volume)
    top_ask:Tuple[float,float] # (price,volume)
    spread:Union[float,None]
    total_bid_volume:float
    total_ask_volume:float
    vwap_bid:Union[float,None]
    vwap_ask:Union[float,None]
    bid_count:int
    ask_count:int
    depth_of_book:dict #{bids: List[Tuple[float, float]], asks: List[Tuple[float, float]]}
    