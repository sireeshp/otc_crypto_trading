from pydantic import Field

from src.models.OrderBookDataModel import PriceVolumePair


class BestPriceData(PriceVolumePair):
    exchange: str = Field(..., description="The exchange where the price is quoted.")
