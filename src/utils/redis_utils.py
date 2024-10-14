import json
from typing import Any, Optional

import aioredis

from src.utils.config import Config
from src.utils.logger import setup_logger

logger = setup_logger("redis_utils", "logs/redis_utils.log")


class RedisCache:
    def __init__(self, expire: int = 60):
        self.expire = expire
        self.redis = None

    def connect(self):
        if not self.redis:
            try:
                self.redis = aioredis.from_url(
                    Config.REDIS_URI, encoding="utf-8", decode_responses=True
                )
                logger.info("Connected to Redis")
            except Exception as e:
                logger.error(f"Failed to connect Redis {e}")

    async def get(self, key: str) -> Optional[Any]:
        try:
            if self.redis is None:
                self.connect()
            cache_data = await self.redis.get(key)
            return json.load(cache_data) if cache_data else None
        except Exception as e:
            logger.error(f"Error retrieving key {key} from Redis: {e}")
            return None

    async def set(self, key: str, value: Any, expire: Optional[int] = None):
        try:
            if key is not None and value is not None:
                if self.redis is None:
                    self.connect()
                expire_time = expire if expire is not None else self.expire
                serialized_value = json.dumps(value)
                await self.redis.set(key, serialized_value, ex=expire_time)
                logger.info(
                    f"Key {key} stored in Redis with expiration {expire_time}s"
                )
        except Exception as e:
            logger.error(f"Error setting key {key} in Redis: {e}")

    async def incr(self, key: str) -> int:
        try:
            if self.redis is None:
                self.connect()
            return await self.redis.incr(key)
        except Exception as e:
            logger.error(f"Error incrementing key {key} in Redis: {e}")
            return 0

    async def close(self):
        if self.redis:
            await self.redis.close()
            logger.info("Closed Redis connection")
