from typing import List, Union

import ccxt.async_support as ccxt
import ccxt.pro as ccxtpro
from ccxt.base.exchange import Exchange

from src.data.exchange_keys import get_exchange_keys
from src.models.ExchangeKey import ExchangeKey
from src.utils.logger import setup_logger

logger = setup_logger("quote_service", "logs/quote_service.log")


def initialize_exchange(
    api: ExchangeKey, ws: bool = False
) -> Union[Exchange, None]:
    if api is None or api.exchange_name.lower() not in ccxt.exchanges:
        return None

    if exchange_class := getattr(
        ccxtpro if ws else ccxt, api.exchange_name.lower(), None
    ):
        return exchange_class(
            {
                "apiKey": api.api_key,
                "secret": api.api_secret,
            }
        )
    return None


# Get all supported exchanges from CCXT
def get_supported_exchanges() -> List[str]:
    """
    Fetches a list of all CCXT supported exchanges.
    :return: List of supported exchange names.
    """
    return ccxt.exchanges


# Dynamically initialize all supported exchanges with their keys
async def initialize_all_exchanges(
    exchange_keys: List[ExchangeKey],
    load_markets: bool = True,
    ws: bool = False,
) -> List[Union[Exchange, None]]:
    """
    Initializes all exchanges based on the provided ExchangeKey list.
    :param exchange_keys: List of ExchangeKey containing exchange names and credentials.
    :return: List of initialized Exchange objects or None for unsupported exchanges.
    """
    initialized_exchanges = []

    for key in exchange_keys:
        if exchange := initialize_exchange(key, ws=ws):
            try:
                if load_markets:
                    await exchange.load_markets()  # Load markets as part of initialization
                initialized_exchanges.append(exchange)
                print(f"Initialized exchange: {key.exchange_name}")
            except Exception as e:
                print(f"Failed to initialize {key.exchange_name}: {e}")
                initialized_exchanges.append(None)
        else:
            print(f"{key.exchange_name} not supported.")
            initialized_exchanges.append(None)

    return initialized_exchanges


async def get_exchange_by_exchange_name(
    exchange_name, ws: bool = False
) -> Exchange:
    exchange_keys = await get_exchange_keys()
    selected_exchange_key = next(
        (
            exchange_key
            for exchange_key in exchange_keys
            if exchange_key.exchange_name.lower() == exchange_name.lower()
        ),
        None,
    )
    if not selected_exchange_key:
        raise ValueError(f"Exchange {exchange_name} not found")
    exchange = initialize_exchange(selected_exchange_key, ws=ws)
    if exchange is None:
        raise ValueError(f"Failed to initialize exchange {exchange_name}")
    return exchange
