from typing import Optional

from pymongo.collection import Collection
from pymongo.errors import PyMongoError

from src.models.FeesModel import Fees
from src.utils.config import Config
from src.utils.logger import setup_logger
from src.utils.mongo_utils import get_db, get_fees_collection

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
        # If DB connection is disabled, return default fees
        if not connect_db:
            return get_default_fees()

        query = {"exchange_name": exchange_name}
        if symbol:
            query["symbol"] = symbol

        # Perform the query to fetch the fee record
        async for db in get_db():
            fee_collection: Collection = get_fees_collection(db)
            fee_record = await fee_collection.find_one(query)

            if fee_record:
                return Fees(
                    symbol=fee_record.get("symbol"),
                    exchange_name=fee_record.get("exchange_name"),
                    taker_fee_percent=fee_record.get(
                        "taker_fee_percent", Config.EXTRA_TAKER_FEE_PERCENTAGE
                    ),
                    maker_fee_percent=fee_record.get(
                        "maker_fee_percent", Config.EXTRA_MAKER_FEE_PERCENTAGE
                    ),
                )

            # Log a warning if no specific fee record was found
            logger.warning(f"No fee record found for query: {query}")

        # Return default fees if no record was found
        return get_default_fees()

    except PyMongoError as pymongo_err:
        logger.error(f"MongoDB error occurred: {pymongo_err}")
        return get_default_fees()

    except Exception as general_err:
        logger.error(f"An unexpected error occurred: {general_err}")
        return get_default_fees()
