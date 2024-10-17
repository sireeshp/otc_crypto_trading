# quote_service.py
import asyncio
from typing import List, Union

import ccxt.async_support as ccxt
from ccxt.base.exchange import Exchange

from src.data.fetch_fees import fetch_fees
from src.models.MarketDataModel import MarketData
from src.models.OHLCVDataModel import OHLCVData
from src.models.OrderBookDataModel import OrderBookData, PriceVolumePair
from src.models.PriceEngineDataModel import BestPriceData, PriceEngineData
from src.models.TickerDataModel import TickerData
from src.services.connect_exchange_service import (
    get_exchange_by_exchange_name,
    get_exchange_keys,
    initialize_exchange,
)
from src.utils.app_utils import normalize_symbol
from src.utils.logger import setup_logger
from src.utils.redis_utils import RedisCache

logger = setup_logger("quote_service", "logs/quote_service.log")
cache = RedisCache()


# Fetch historical data
async def fetch_historical_data(
    symbol: str = "BTC/USD",
    timeframe: str = "1h",
    since: Union[int, None] = None,
) -> Union[List[OHLCVData], None]:
    try:
        cache_key = f"historical_data:{symbol}:{timeframe}:{since}"
        cached_data = await cache.get(
            cache_key,
        )
        if cached_data:
            return cached_data

        exchanges = await get_exchange_keys()
        exchange = initialize_exchange(exchanges[0])
        if exchange is not None:
            ex_symbol = normalize_symbol(symbol)
            ohlcv_data = await exchange.fetch_ohlcv(ex_symbol, timeframe, since=since)
            ohlcv_list: List[OHLCVData] = [
                OHLCVData(
                    timestamp=ohlcv[0],
                    open=ohlcv[1],
                    high=ohlcv[2],
                    low=ohlcv[3],
                    close=ohlcv[4],
                    volume=ohlcv[5],
                )
                for ohlcv in ohlcv_data
            ]
        if timeframe.endswith("m"):
            cache_expire_time = int(timeframe[:-1]) * 60  # minutes
        elif timeframe.endswith("h"):
            cache_expire_time = int(timeframe[:-1]) * 3600  # hours
        elif timeframe.endswith("d"):
            cache_expire_time = int(timeframe[:-1]) * 86400  # days
        else:
            cache_expire_time = 3600  # Default to 1 hour
        await cache.set(cache_key, ohlcv_list, expire=cache_expire_time)
        return ohlcv_list
    except Exception as e:
        logger.error(f"Error fetching historical data: {e}")
    finally:
        await exchange.close()
    return None


# Fetch real-time ticker data
async def fetch_ticker(symbol="BTC/USD") -> Union[TickerData, None]:
    exchanges = await get_exchange_keys()
    exchange = initialize_exchange(exchanges[0])
    if exchange is not None:
        try:
            ex_symbol = normalize_symbol(symbol)
            ticker = await exchange.fetch_ticker(ex_symbol)
            return TickerData(
                symbol=ticker["symbol"],
                high=ticker["high"],
                low=ticker["low"],
                bid=ticker["bid"],
                bidVolume=ticker["bidVolume"],
                ask=ticker["ask"],
                askVolume=ticker["askVolume"],
                vwap=ticker["vwap"],
                open=ticker["open"],
                close=ticker["close"],
                previousClose=ticker["previousClose"],
                change=ticker["change"],
                percentage=ticker["percentage"],
                average=ticker["average"],
                baseVolume=ticker["baseVolume"],
                quoteVolume=ticker["quoteVolume"],
                last=ticker["last"],
                datetime=ticker["datetime"],
            )
        except ccxt.BaseError as e:
            logger.error(f"Error fetching ticker: {e}")
        finally:
            await exchange.close()
    return None


# Calculate VWAP (Volume Weighted Average Price)
def calculate_vwap(
    order_book_side: List[List[Union[float, int]]]
) -> Union[float, None]:
    try:
        if order_book_side is not None:
            total_volume = 0
            weighted_price_sum = 0
            for entry in order_book_side:
                price, volume = entry[0], entry[1]
                total_volume += volume
                weighted_price_sum += price * volume
            return None if total_volume == 0 else weighted_price_sum / total_volume
    except Exception as e:
        logger.error(f"Error calculate_vwap: {e}")
    return None


async def fetch_order_book(
    exchange_name: str = "Kraken", symbol="BTC/USD"
) -> Union[OrderBookData, None]:
    try:
        # Normalize symbol format
        ex_symbol = normalize_symbol(symbol)

        # Find the exchange by name
        exchange_keys = await get_exchange_keys()
        exchange_to_connect = next(
            (
                ex_key
                for ex_key in exchange_keys
                if ex_key.exchange_name == exchange_name
            ),
            None,
        )

        if not exchange_to_connect:
            logger.error(f"Exchange {exchange_name} not found.")
            return None

        # Initialize exchange connection
        exchange = initialize_exchange(exchange_to_connect)
        if not exchange:
            logger.error(f"Failed to initialize exchange {exchange_name}")
            return None

        return await get_order_book_model(exchange, ex_symbol)
    except Exception as e:
        logger.error(
            f"Error fetching order book for {symbol} from {exchange_name}: {e}"
        )
        return None

    finally:
        if exchange:
            await exchange.close()


async def get_order_book_model(
    exchange: Exchange, symbol
) -> Union[OrderBookData, None]:
    try:
        ex_symbol = normalize_symbol(symbol)
        order_book = await exchange.fetch_order_book(ex_symbol)
        sorted_bids = sorted(order_book["bids"], key=lambda x: x[0], reverse=True)
        sorted_asks = sorted(order_book["asks"], key=lambda x: x[0])

        top_ask = sorted_asks[0] if len(sorted_asks) > 0 else [None, None]
        top_bid = sorted_bids[0] if len(sorted_bids) > 0 else [None, None]
        spread = (
            round(top_ask[0] - top_bid[0], 5) if top_bid[0] and top_ask[0] else None
        )

        total_bid_volume = sum(bid[1] for bid in sorted_bids)
        total_ask_volume = sum(ask[1] for ask in sorted_asks)
        vwap_bid = calculate_vwap(sorted_bids)
        vwap_ask = calculate_vwap(sorted_asks)

        return OrderBookData(
            top_bid=(
                PriceVolumePair(price=top_bid[0], volume=top_bid[1])
                if top_bid[0]
                else None
            ),
            top_ask=(
                PriceVolumePair(price=top_ask[0], volume=top_ask[1])
                if top_ask[0]
                else None
            ),
            spread=spread,
            total_bid_volume=total_bid_volume,
            total_ask_volume=total_ask_volume,
            vwap_bid=vwap_bid,
            vwap_ask=vwap_ask,
            bid_count=len(sorted_bids),
            ask_count=len(sorted_asks),
            depth_of_book={"bids": sorted_bids, "asks": sorted_asks},
        )
    except Exception as e:
        logger.error(f"get_order_book_model {e}")
        return None


async def fetch_ticker_depth(
    symbol: str = "BTC/USD", exchange_name: str = "Kraken", depth: int = 5
):
    ticker_data = await fetch_ticker(symbol)
    order_book = await fetch_order_book(exchange_name, symbol)
    return {
        "ticker": ticker_data,
        "order_book_depth": {
            "bids": order_book.depth_of_book["bids"][:depth],
            "asks": order_book.depth_of_book["asks"][:depth],
        },
    }


async def aggregated_market_data(symbol="BTC/USD") -> PriceEngineData:
    best_bid = None
    best_ask = None
    best_bid_exchange = None
    best_ask_exchange = None
    exchange_data: List[OrderBookData] = []
    try:
        exchanges = await get_exchange_keys()
        ex_symbol = normalize_symbol(symbol)
        for api_keys in exchanges:
            book = await fetch_order_book(api_keys.exchange_name, ex_symbol)
            if book is not None:
                if best_bid is None or book.top_bid.price > best_bid.price:
                    best_bid = book.top_bid
                    best_bid_exchange = api_keys.exchange_name

                if best_ask is None or book.top_ask.price < best_ask.price:
                    best_ask = book.top_ask
                    best_ask_exchange = api_keys.exchange_name

                exchange_data.append(book)
        exchange_data = sorted(
            exchange_data, key=lambda x: x.top_bid.price, reverse=True
        )
        return PriceEngineData(
            best_bid=BestPriceData(**best_bid.model_dump(), exchange=best_bid_exchange),
            best_ask=BestPriceData(**best_ask.model_dump(), exchange=best_ask_exchange),
            exchange_data=exchange_data,
        )
    except Exception as e:
        logger.error(f"price_engine {e}")


async def fetch_tickers(
    exchange_name: str = "Kraken",
):
    exchange = None
    try:
        exchange = await get_exchange_by_exchange_name(exchange_name)
        tickers = await exchange.fetch_tickers()
        ticker_data_list = []
        for symbol, ticker in tickers.items():
            ticker_data = TickerData(
                symbol=ticker["symbol"],
                high=ticker["high"],
                low=ticker["low"],
                bid=ticker["bid"],
                bidVolume=ticker["bidVolume"],
                ask=ticker["ask"],
                askVolume=ticker["askVolume"],
                vwap=ticker["vwap"],
                open=ticker["open"],
                close=ticker["close"],
                last=ticker["last"],
                previousClose=ticker["previousClose"],
                change=ticker["change"],
                percentage=ticker["percentage"],
                average=ticker["average"],
                baseVolume=ticker["baseVolume"],
                quoteVolume=ticker["quoteVolume"],
                datetime=ticker["datetime"],
            )
            ticker_data_list.append(ticker_data)
        return ticker_data_list
    except Exception as e:
        logger.error(f"fetch_tickers {e}")
        return None
    finally:
        if exchange:
            await exchange.close()


async def load_markets(exchange_name: str = "Kraken", reload: bool = False):
    exchange = None
    try:
        fee = await fetch_fees()
        exchange: Exchange = await get_exchange_by_exchange_name(exchange_name)
        markets = await exchange.load_markets(reload)
        market_data = []
        for symbol, entry in markets.items():
            market = MarketData.model_construct(**entry)
            market.taker = round(market.taker * (1 + fee.taker_fee_percent), 5)
            market.maker = round(market.maker * (1 + fee.maker_fee_percent), 5)
            market_data.append(market)
        return market_data
    except Exception as e:
        logger.error(f"load_markets {e}")
        return None
    finally:
        if exchange:
            await exchange.close()


async def fetch_market_summary(
    exchange_name: str = "Kraken",
) -> Union[dict, None]:
    try:
        exchange = await get_exchange_by_exchange_name(exchange_name)
        return await exchange.fetch_markets()
    except Exception as e:
        logger.error(f"Error fetching market summary: {e}")
        return None
    finally:
        if exchange:
            await exchange.close()


async def fetch_funding_rate(
    exchange_name: str = "Kraken", symbol: str = "BTC/USD"
) -> Union[dict, None]:
    try:
        exchange = await get_exchange_by_exchange_name(exchange_name)
        return await exchange.fetch_funding_rate(symbol)
    except Exception as e:
        logger.error(f"Error fetching funding rate for {symbol}: {e}")
        return None
    finally:
        if exchange:
            await exchange.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    # Fetch historical data
    historical_data = loop.run_until_complete(fetch_historical_data())
    print("Historical Data:", historical_data)

    if ticker_data := loop.run_until_complete(fetch_ticker()):
        print(f"Ticker Data: {ticker_data}")

    # Run the price engine
    price_summary = loop.run_until_complete(aggregated_market_data("BTC/USD"))
    print(f"Best Bid: {price_summary.best_bid}")
    print(f"Best Ask: {price_summary.best_ask}")
