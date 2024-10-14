from typing import List

from pymongo.errors import ConnectionFailure, PyMongoError

from src.models.ExchangeKey import ExchangeKey
from src.utils.config import Config
from src.utils.logger import setup_logger
from src.utils.mongo_utils import check_db_connection, get_db

logger = setup_logger("exchange_keys", "logs/exchange_keys.log")
connect_db = Config.CONNECT_DB


async def get_exchange_keys() -> List[ExchangeKey]:
    defaultCon = [
        ExchangeKey(
            api_key=Config.KRAKEN_API_KEY,
            api_secret=Config.KRAKEN_PRIVATE_KEY,
            exchange_name="Kraken",
        )
    ]
    print(connect_db)
    if connect_db:
        try:
            if not await check_db_connection():
                return None
            db = get_db()
            exchange_keys = []
            async for collect in db.apiKeys.find({}):
                exchange_keys.append(
                    ExchangeKey(
                        api_key=collect["api_key"],
                        api_secret=collect["api_secret"],
                        exchange_name=collect["exchange_name"],
                    )
                )
            return exchange_keys
        except ConnectionFailure as conn_err:
            logger.error(
                f"Error: Unable to connect to the MongoDB server: {conn_err}"
            )
            return defaultCon
        except PyMongoError as pymongo_err:
            logger.error(f"MongoDB error occurred: {pymongo_err}")
            return defaultCon
        except Exception as general_err:
            logger.error(f"An unexpected error occurred: {general_err}")
            return defaultCon
    return defaultCon
