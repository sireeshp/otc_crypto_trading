from fastapi import APIRouter, HTTPException
from src.data.quote_data import (
    fetch_historical_data,
    fetch_ticker,
    aggregated_market_data,
)
from src.models.TickerData import TickerData
from src.models.PriceEngineData import PriceEngineData
from src.models.OrderBookData import OrderBookData
from typing import List
from src.models.OHLCVData import OHLCVData
router = APIRouter()


@router.get("/ticker/{symbol}", response_model=TickerData)
async def get_ticker(symbol: str = "BTC/USD"):
    """
    Retrieves the ticker data for a specified cryptocurrency symbol.
    If the ticker data is not found, it raises a 404 HTTP exception.

    This asynchronous function fetches the ticker information for the given symbol and returns it in the response.
    If an error occurs during the fetching process or if the ticker data is not available, it raises an appropriate
    HTTP exception with a relevant status code and message.

    Args:
        symbol (str): The cryptocurrency symbol for which to fetch the ticker data. Defaults to 'BTC/USD'.

    Returns:
        TickerData: The ticker data for the specified cryptocurrency symbol.

    Raises:
        HTTPException: If the ticker data is not found, a 404 status code is raised.
                       If any other error occurs, a 500 status code is raised.
    """

    try:
        ticker_data = await fetch_ticker(symbol)
        if ticker_data is None:
            raise HTTPException(
                status_code=404, detail=f"Ticker data not found for {symbol}"
            )
        return ticker_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/historical/{symbol}", response_model=List[OHLCVData])
async def get_historical_data(
    symbol: str = "BTC/USD", time_frame: str = "1h", since: int = None
):
    """
    Retrieves historical data for a specified cryptocurrency symbol over a given time frame.
    If the historical data is not found, it raises a 404 HTTP exception.

    This asynchronous function fetches historical market data for the specified symbol, time frame, and optional
    starting point. If the data is unavailable or an error occurs during the fetching process, it raises an
    appropriate HTTP exception with a relevant status code and message.

    Args:
        symbol (str): The cryptocurrency symbol for which to fetch historical data. Defaults to 'BTC/USD'.
        time_frame (str): The time frame for the historical data. Defaults to '1h'.
        since (int): An optional parameter to specify the starting point for the historical data.

    Returns:
        HistoricalData: The historical data for the specified cryptocurrency symbol.

    Raises:
        HTTPException: If the historical data is not found, a 404 status code is raised.
                       If any other error occurs, a 500 status code is raised.
    """

    try:
        historical_data = await fetch_historical_data(symbol, time_frame, since)
        if historical_data is None:
            raise HTTPException(
                status_code=404, detail=f"Historical data not found for {symbol}"
            )
        return historical_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

@router.get('/historical/{symbol}', response_model=PriceEngineData)
async def get_historical_data(symbol: str = 'BTC/USD', time_frame: str = '1h', since: int = None):
    """
    Retrieves historical data for a specified cryptocurrency symbol over a given time frame. 
    If the historical data is not found, it raises a 404 HTTP exception.

    This asynchronous function fetches historical market data for the specified symbol, time frame, and optional 
    starting point. If the data is unavailable or an error occurs during the fetching process, it raises an 
    appropriate HTTP exception with a relevant status code and message.

    Args:
        symbol (str): The cryptocurrency symbol for which to fetch historical data. Defaults to 'BTC/USD'.
        time_frame (str): The time frame for the historical data. Defaults to '1h'.
        since (int): An optional parameter to specify the starting point for the historical data.

    Returns:
        HistoricalData: The historical data for the specified cryptocurrency symbol.

    Raises:
        HTTPException: If the historical data is not found, a 404 status code is raised. 
                       If any other error occurs, a 500 status code is raised.
    """

    try:
        aggregate_data = await aggregated_market_data(symbol)
        if aggregate_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"Aggregate Market data is not found for {symbol}",
            )
        return aggregate_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
