from typing import List, Optional

from pydantic import BaseModel


# Precision Model
class Precision(BaseModel):
    amount: Optional[float]
    price: Optional[float]
    cost: Optional[float]
    base: Optional[float]
    quote: Optional[float]


# Limits Model
class LimitsLeverage(BaseModel):
    min: Optional[float]
    max: Optional[float]


class LimitsAmount(BaseModel):
    min: Optional[float]
    max: Optional[float]


class LimitsPrice(BaseModel):
    min: Optional[float]
    max: Optional[float]


class LimitsCost(BaseModel):
    min: Optional[float]
    max: Optional[float]


class Limits(BaseModel):
    leverage: Optional[LimitsLeverage]
    amount: Optional[LimitsAmount]
    price: Optional[LimitsPrice]
    cost: Optional[LimitsCost]


# Margin Modes Model
class MarginModes(BaseModel):
    cross: Optional[str]
    isolated: Optional[str]


# Info Model
class Info(BaseModel):
    altname: Optional[str]
    wsname: Optional[str]
    aclass_base: Optional[str]
    base: Optional[str]
    aclass_quote: Optional[str]
    quote: Optional[str]
    lot: Optional[str]
    cost_decimals: Optional[str]
    pair_decimals: Optional[str]
    lot_decimals: Optional[str]
    lot_multiplier: Optional[str]
    leverage_buy: Optional[List[float]]
    leverage_sell: Optional[List[float]]
    fees: Optional[List[List[str]]]
    fees_maker: Optional[List[List[str]]]
    fee_volume_currency: Optional[str]
    margin_call: Optional[str]
    margin_stop: Optional[str]
    ordermin: Optional[str]
    costmin: Optional[str]
    tick_size: Optional[str]
    status: Optional[str]


# Main Market Data Model
class MarketData(BaseModel):
    id: str
    symbol: str
    base: str
    quote: str
    baseId: str
    quoteId: str
    type: str
    spot: bool
    margin: bool
    swap: bool
    future: bool
    option: bool
    active: bool
    contract: bool
    taker: float
    maker: float
