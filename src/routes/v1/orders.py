from fastapi import APIRouter, HTTPException

from src.models.OrderBookData import OrderBookData
from src.services.quote_service import fetch_order_book

router = APIRouter()


@router.get(
    "/order_book/{exchange_name}/{symbol}", response_model=OrderBookData
)
async def get_order_book(exchange_name: str = "Kraken", symbol: str = "BTCUSD"):
    try:
        order_book = await fetch_order_book(exchange_name, symbol)
        if order_book is None:
            raise HTTPException(
                status_code=404,
                detail=f"Order book not found for symbol {symbol}",
            )
        return order_book
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
