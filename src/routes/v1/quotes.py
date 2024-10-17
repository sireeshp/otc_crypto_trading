from typing import List

from fastapi import APIRouter, HTTPException

from src.models.OHLCVDataModel import OHLCVData
from src.models.PriceEngineDataModel import PriceEngineData
from src.models.TickerDataModel import TickerData
from src.services.quote_service import (
    aggregated_market_data,
    fetch_historical_data,
    fetch_ticker,
    fetch_tickers,
    load_markets,
)

router = APIRouter()


@router.get("/ticker/{symbol}", response_model=TickerData)
async def get_ticker(symbol: str = "BTCUSD"):
    """
    Retrieves the ticker data for a specified cryptocurrency symbol.
    If the ticker data is not found, it raises a 404 HTTP exception.

    This asynchronous function fetches the ticker information for the given symbol and returns it in the response.
    If an error occurs during the fetching process or if the ticker data is not available, it raises an appropriate
    HTTP exception with a relevant status code and message.

    Args:
        symbol (str): The cryptocurrency symbol for which to fetch the ticker data. Defaults to 'BTCUSD'.

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
    symbol: str = "BTCUSD", time_frame: str = "1h", since: int = None
):
    """
    Retrieves historical data for a specified cryptocurrency symbol over a given time frame.
    If the historical data is not found, it raises a 404 HTTP exception.

    This asynchronous function fetches historical market data for the specified symbol, time frame, and optional
    starting point. If the data is unavailable or an error occurs during the fetching process, it raises an
    appropriate HTTP exception with a relevant status code and message.

    Args:
        symbol (str): The cryptocurrency symbol for which to fetch historical data. Defaults to 'BTCUSD'.
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
                status_code=404,
                detail=f"Historical data not found for {symbol}",
            )
        return historical_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/aggregated/{symbol}", response_model=PriceEngineData)
async def get_aggregated_market_data(symbol: str = "BTCUSD"):
    """
    Retrieves historical data for a specified cryptocurrency symbol over a given time frame.
    If the historical data is not found, it raises a 404 HTTP exception.

    This asynchronous function fetches historical market data for the specified symbol, time frame, and optional
    starting point. If the data is unavailable or an error occurs during the fetching process, it raises an
    appropriate HTTP exception with a relevant status code and message.

    Args:
        symbol (str): The cryptocurrency symbol for which to fetch historical data. Defaults to 'BTCUSD'.
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


@router.get("/exchange_tickers/{exchange_name}", response_model=List[TickerData])
async def get_exchange_tickers(exchange_name: str = "Kraken"):
    """
    Retrieves the ticker data for all cryptocurrencies available on a specified exchange.
    If no tickers are found for the given exchange, it raises a 404 HTTP exception.

    This asynchronous function fetches the ticker information for the specified exchange and returns it in the response.
    If an error occurs during the fetching process or if no tickers are available, it raises an appropriate
    HTTP exception with a relevant status code and message.

    Args:
        exchange_name (str): The name of the exchange for which to fetch ticker data. Defaults to "Kraken".

    Returns:
        List[TickerData]: A list of ticker data for the specified exchange.

    Raises:
        HTTPException: If no tickers are found for the specified exchange, a 404 status code is raised.
                       If any other error occurs, a 500 status code is raised.
    """
    try:
        tickers = await fetch_tickers(exchange_name)
        if tickers is None:
            raise HTTPException(
                status_code=404,
                detail=f"No tickers found for {exchange_name}",
            )
        return tickers
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/markets/{exchange_name}")
async def get_markets(exchange_name: str = "Kraken"):
    try:
        markets = await load_markets(exchange_name)
        if markets is None:
            raise HTTPException(
                f"Notable to load markets for the exchange {exchange_name} "
            )
        return markets
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
