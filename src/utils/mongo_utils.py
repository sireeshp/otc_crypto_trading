from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure

from src.utils.config import Config
from src.utils.logger import setup_logger

logger = setup_logger("mongo", "logs/mongo.log")


async def get_db():
    client = AsyncIOMotorClient(Config.MONGO_URI)
    try:
        yield client[Config.MONGO_DATA_BASE]
    except ConnectionFailure as e:
        logger.error(f"MongoDB Connection Error: {e}")
        raise ValueError("Cannot connect to MongoDB") from e
    finally:
        client.close()


def get_otp_collection(db: AsyncIOMotorDatabase) -> Collection:
    return db.get_collection("otps")


def get_users_collection(db: AsyncIOMotorDatabase) -> Collection:
    return db.get_collection("users")


def get_fees_collection(db: AsyncIOMotorDatabase) -> Collection:
    return db.get_collection("fees")


def get_api_keys_collection(db: AsyncIOMotorDatabase) -> Collection:
    return db.get_collection("api_keys")
