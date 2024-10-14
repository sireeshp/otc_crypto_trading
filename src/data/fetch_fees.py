from typing import Optional

from pymongo.errors import PyMongoError

from src.models.Fees import Fees
from src.utils.config import Config
from src.utils.logger import setup_logger
from src.utils.mongo_utils import check_db_connection, get_db

logger = setup_logger("fetch_fees", "logs/fetch_fees.log")
connect_db = Config.CONNECT_DB


# Default fee structure to return if no DB connection or no specific record
def get_default_fees() -> Fees:
    return Fees(
        symbol=None,
        exchange_name="Kraken",
        taker_fee_percent=Config.EXTRA_TAKER_FEE_PERCENTAGE,
        maker_fee_percent=Config.EXTRA_MAKER_FEE_PERCENTAGE,
    )


# Function to fetch fees from DB or return default
async def fetch_fees(
    exchange_name: str = "Kraken", symbol: Optional[str] = None
) -> Fees:
    try:
        if not connect_db:
            return get_default_fees()
        # Check if the DB connection is established
        if not await check_db_connection():
            return get_default_fees()

        query = {"exchange_name": exchange_name}

        # If symbol is provided, look for that specific symbol
        if symbol is not None:
            query["symbol"] = symbol

        # Perform the query to fetch the fee record
        db = get_db()
        fee_record = await db.fees.find_one(query)

        if fee_record:
            return Fees(
                symbol=fee_record["symbol"],
                exchange_name=fee_record["exchange_name"],
                taker_fee_percent=fee_record["taker_fee_percent"],
                maker_fee_percent=fee_record["market_fee_percent"],
            )

        logger.warning(
            f"No fee record found for exchange: {exchange_name}, symbol: {symbol}"
        )
        # Return the default fee record if no specific record found
        return get_default_fees()

    except PyMongoError as pymongo_err:
        logger.error(f"MongoDB error occurred: {pymongo_err}")
        return get_default_fees()

    except Exception as general_err:
        logger.error(f"An unexpected error occurred: {general_err}")
        return get_default_fees()
