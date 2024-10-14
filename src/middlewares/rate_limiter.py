import aioredis
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, HTTPException, Response
from src.utils.config import Config
import logging

logger = logging.getLogger(__name__)

class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, rate_limit: int = 60, window: int = 60):
        super().__init__(app)
        self.rate_limit = rate_limit  # Max number of requests allowed per window
        self.window = window  # Time window in seconds
        self.redis = None

    async def dispatch(self, request: Request, call_next) -> Response:
        # Initialize Redis connection pool
        if self.redis is None:
            try:
                 self.redis = aioredis.from_url(Config.REDIS_URI, encoding="utf-8", decode_responses=True)
            except Exception as e:
                logger.error(f"Error connecting to Redis: {e}")
                return Response(status_code=500, content="Internal server error")

        client_ip = request.client.host
        redis_key = f"rate_limit:{client_ip}"

        try:
            # Get current request count from Redis
            current_count = await self.redis.get(redis_key)

            if current_count is None:
                # First request, set the initial count to 1 and set the expiration time
                await self.redis.set(redis_key, 1, ex=self.window)
            else:
                current_count = int(current_count)
                if current_count >= self.rate_limit:
                    # Exceeded rate limit
                    raise HTTPException(status_code=429, detail="Too many requests, please slow down.")
                else:
                    # Increment the request count
                    await self.redis.incr(redis_key)
            return await call_next(request)
        except Exception as e:
            logger.error(f"Error during rate limiting: {e}")
            return Response(status_code=500, content="Internal server error")

    async def close(self):
        """Close Redis connection pool gracefully when shutting down."""
        if self.redis is not None:
            self.redis.close()
            await self.redis.wait_closed()
