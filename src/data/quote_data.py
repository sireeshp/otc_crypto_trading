import ccxt.async_support as ccxt
import asyncio
import logging
from src.db.exchange_keys import get_exchange_keys
from ccxt.base.exchange import Exchange
from typing import Union, List
from src.models.TickerData import TickerData
from src.models.PriceEngineData import PriceEngineData, BestPriceData
from src.models.OrderBookData import OrderBookData

# Set up logging for production
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Initialize the exchange using environment variables
def initialize_exchange(api) -> Union[Exchange, None]:
    if api is not None and api.exchange_name == "Kraken":  # Access with dot notation
        return ccxt.kraken(
            {
                "apiKey": api.api_key,
                "secret": api.api_secret,
            }
        )
    return None


# Fetch historical data
async def fetch_historical_data(
    symbol: str = "BTC/USD", timeframe: str = "1h", since: Union[int, None] = None
) -> List[List[Union[int, float]]]:
    try:
        exchanges = await get_exchange_keys()
        exchange = initialize_exchange(exchanges[0])
        if exchange is not None:
            return await exchange.fetch_ohlcv(symbol, timeframe, since=since)
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
            ticker = await exchange.fetch_ticker(symbol)
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


# Fetch order book and return model
async def fetch_order_book(
    exchange=None, symbol="BTC/USD"
) -> Union[OrderBookData, None]:
    try:
        if exchange is None:
            exchanges = await get_exchange_keys()
            exchange = initialize_exchange(exchanges[0])
        return (
            await get_order_book_model(exchange, symbol)
            if exchange is not None
            else None
        )
    except Exception as e:
        logger.error(f"fetch_order_book {e}")
    finally:
        await exchange.close()
    return None


async def get_order_book_model(exchange, symbol) -> OrderBookData:
    order_book = await exchange.fetch_order_book(symbol)
    sorted_bids = sorted(order_book["bids"], key=lambda x: x[0], reverse=True)
    sorted_asks = sorted(order_book["asks"], key=lambda x: x[0])

    top_ask = sorted_asks[0] if len(sorted_asks) > 0 else [None, None]
    top_bid = sorted_bids[0] if len(sorted_bids) > 0 else [None, None]
    spread = round(top_ask[0] - top_bid[0], 5) if top_bid[0] and top_ask[0] else None

    total_bid_volume = sum(bid[1] for bid in sorted_bids)
    total_ask_volume = sum(ask[1] for ask in sorted_asks)
    vwap_bid = calculate_vwap(sorted_bids)
    vwap_ask = calculate_vwap(sorted_asks)

    return OrderBookData(
        top_bid=(top_bid[0], top_bid[1]),
        top_ask=(top_ask[0], top_ask[1]),
        spread=spread,
        total_bid_volume=total_bid_volume,
        total_ask_volume=total_ask_volume,
        vwap_bid=vwap_bid,
        vwap_ask=vwap_ask,
        bid_count=len(sorted_bids),
        ask_count=len(sorted_asks),
        depth_of_book={"bids": sorted_bids, "asks": sorted_asks},
    )


async def aggregated_market_data(symbol="BTC/USD") -> PriceEngineData:
    best_bid = None
    best_ask = None
    best_bid_exchange = None
    best_ask_exchange = None
    exchange_data :List[OrderBookData] = []
    try:
        exchanges = await get_exchange_keys()
        for api_keys in exchanges:
            exchange = initialize_exchange(api_keys)
            book = await fetch_order_book(exchange, symbol)
            if book is not None:
                if best_bid is None or book.top_bid[0] > best_bid[0]:
                    best_bid = book.top_bid
                    best_bid_exchange = api_keys.exchange_name

                if best_ask is None or book.top_ask[0] < best_ask[0]:
                    best_ask = book.top_ask
                    best_ask_exchange = api_keys.exchange_name

                exchange_data.append(book)
        exchange_data = sorted(exchange_data,key=lambda x:x.top_bid[0],reverse=True)
        return PriceEngineData(
            best_bid=BestPriceData(price=best_bid, exchange=best_bid_exchange),
            best_ask=BestPriceData(price=best_ask, exchange=best_ask_exchange),
            exchange_data=exchange_data,
        )
    except Exception as e:
        logger.error(f"price_engine {e}")


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
