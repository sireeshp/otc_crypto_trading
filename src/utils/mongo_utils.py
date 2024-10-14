
import motor.motor_asyncio
from pymongo.errors import ConnectionFailure

from src.utils.config import Config
from src.utils.logger import setup_logger

logger = setup_logger("mongo", "logs/mongo.log")


# Function to return the database instance
def get_db():
    client = motor.motor_asyncio.AsyncIOMotorClient(Config.MONGO_URI)
    return client[Config.MONGO_DATA_BASE]


async def check_db_connection():
    try:
        # Ensure that MongoDB is available
        db = get_db()  # Use the get_db function to get the database instance
        await db.command(
            "ping"
        )  # Ping the database to ensure connection is available
        return True
    except ConnectionFailure as conn_err:
        logger.error(f"Error: Unable to connect to MongoDB server: {conn_err}")
        return False
