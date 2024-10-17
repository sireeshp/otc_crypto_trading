from typing import List, Union

import ccxt.async_support as ccxt
import ccxt.pro as ccxtpro
from ccxt.base.exchange import Exchange
from pymongo.errors import ConnectionFailure, PyMongoError

from src.models.ExchangeKeyModel import ExchangeKey
from src.utils.config import Config
from src.utils.logger import setup_logger
from src.utils.mongo_utils import get_db

logger = setup_logger("connect_exchange_service", "logs/connect_exchange_service.log")


def initialize_exchange(api: ExchangeKey, ws: bool = False) -> Union[Exchange, None]:
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
    return ccxt.exchanges


# Dynamically initialize all supported exchanges with their keys
async def initialize_all_exchanges(
    exchange_keys: List[ExchangeKey],
    load_markets: bool = True,
    ws: bool = False,
) -> List[Union[Exchange, None]]:
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


async def get_exchange_by_exchange_name(exchange_name, ws: bool = False) -> Exchange:
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


async def get_exchange_keys() -> List[ExchangeKey]:
    connect_db = Config.CONNECT_DB
    defaultCon = [
        ExchangeKey(
            api_key=Config.KRAKEN_API_KEY,
            api_secret=Config.KRAKEN_PRIVATE_KEY,
            exchange_name="Kraken",
        )
    ]

    # Only connect to DB if the `connect_db` flag is True
    if not connect_db:
        return defaultCon

    try:
        exchange_keys = []
        async for db in get_db():
            async for collect in db.apiKeys.find({}):
                exchange_keys.append(
                    ExchangeKey(
                        api_key=collect["api_key"],
                        api_secret=collect["api_secret"],
                        exchange_name=collect["exchange_name"],
                    )
                )
        # Return collected exchange keys
        return exchange_keys or defaultCon

    except ConnectionFailure as conn_err:
        logger.error(f"Error: Unable to connect to the MongoDB server: {conn_err}")
        return defaultCon

    except PyMongoError as pymongo_err:
        logger.error(f"MongoDB error occurred: {pymongo_err}")
        return defaultCon

    except Exception as general_err:
        logger.error(f"An unexpected error occurred: {general_err}")
        return defaultCon
