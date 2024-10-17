from typing import Dict, Optional

from pydantic import BaseModel, Field


class PriceVolumePair(BaseModel):
    price: float = Field(..., description="The price of the bid or ask.")
    volume: float = Field(..., description="The volume for the bid or ask.")


class OrderBookData(BaseModel):
    top_bid: Optional[PriceVolumePair] = Field(
        None, description="List of [price, volume] pairs for the top bids."
    )
    top_ask: Optional[PriceVolumePair] = Field(
        None, description="List of [price, volume] pairs for the top asks."
    )
    spread: Optional[float] = Field(
        None,
        description="The difference between the top ask and top bid prices.",
    )
    total_bid_volume: float = Field(..., description="Total volume of all bids.")
    total_ask_volume: float = Field(..., description="Total volume of all asks.")
    vwap_bid: Optional[float] = Field(
        None, description="Volume Weighted Average Price (VWAP) for bids."
    )
    vwap_ask: Optional[float] = Field(
        None, description="Volume Weighted Average Price (VWAP) for asks."
    )
    bid_count: int = Field(
        ..., description="The total number of bids in the order book."
    )
    ask_count: int = Field(
        ..., description="The total number of asks in the order book."
    )
    depth_of_book: Optional[Dict] = Field(
        ...,
        description="Depth of book with bids and asks as lists of price,volume and timestamp tuples.",
    )
