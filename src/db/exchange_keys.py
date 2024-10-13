import motor.motor_asyncio
from pymongo.errors import PyMongoError, ConnectionFailure
from src.utils.config import Config
from src.models.ExchangeKey import ExchangeKey
from typing import List
client = motor.motor_asyncio.AsyncIOMotorClient(Config.MONGO_URI)
db = client[Config.MONGO_DATA_BASE]
connect_db=False
async def get_exchange_keys()->List[ExchangeKey]:
    """
    Asynchronously retrieves a list of exchange keys from a MongoDB collection. 
    If the connection fails or an error occurs, it returns a default exchange key for Kraken.

    This function attempts to connect to the MongoDB server and fetches API keys stored in the "api_keys" collection. 
    If successful, it constructs and returns a list of `ExchangeKey` objects. In case of any connection or database errors, 
    it logs the error and returns a default exchange key for Kraken.

    Returns:
        List[ExchangeKey]: A list of `ExchangeKey` objects containing the API keys and secrets for the exchanges, 
                            or a default key if an error occurs.
    """
    defaultCon =[ExchangeKey(
        api_key=Config.KRAKEN_API_KEY,
        api_secret=Config.KRAKEN_PRIVATE_KEY,
        exchange_name='Kraken'
    )]
    if(connect_db):
        try:
            await client.server_info()
            collection = db["api_keys"]
            exchange_keys = []
            async for collect in collection.find({}):
                    exchange_keys.append(ExchangeKey(
                        api_key= collect['api_key'],
                        api_secret= collect['api_secret'],
                        exchange_name= collect['exchange_name'],
                    ))
            return exchange_keys
        except ConnectionFailure as conn_err:
                print(f"Error: Unable to connect to the MongoDB server: {conn_err}")
                return defaultCon
        except PyMongoError as pymongo_err:
                print(f"MongoDB error occurred: {pymongo_err}")
                return defaultCon
        except Exception as general_err:
            print(f"An unexpected error occurred: {general_err}")
            return defaultCon
    return defaultCon
    