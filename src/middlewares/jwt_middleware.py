from datetime import datetime, timezone

import jwt
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from src.services.auth_service import get_user_by_id
from src.utils.config import Config
from src.utils.logger import setup_logger
from src.utils.mongo_utils import get_db

logger = setup_logger("jwt_middleware", "logs/jwt_middleware.log")

EXCLUDED_PATHS = [
    "/",
    "/auth/login",
    "/auth/register",
    "/auth/send_otp",
    "/auth/verify_otp",
    "/auth/forgot_password",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/favicon.ico",
]

SECRET_KEY = Config.AUTH_SECURITY_KEY
ALGORITHM = Config.ALGORITHM


class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        # Log the incoming request path
        logger.info(f"Processing request path: {request.url.path}")
        url_path = request.url.path
        if "/api/v1" in url_path:
            url_path = url_path.replace("/api/v1", "")
        print(url_path)
        if url_path in EXCLUDED_PATHS:
            logger.info(f"Skipping JWT authentication for {request.url.path}")
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            logger.warning("Authorization header missing or invalid")
            return JSONResponse(
                status_code=401,
                content={"message": "Authorization header missing or invalid"},
            )

        token = auth_header.split(" ")[1]
        print(token)
        try:
            # Decode JWT token
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            print(payload)
            logger.info("JWT token decoded successfully")

            # Check if token has expired
            if payload.get("exp") < datetime.now(timezone.utc).timestamp():
                logger.warning(f"Token expired for user: {payload.get('sub')}")
                raise HTTPException(status_code=401, detail="Token expired")

            user_id = payload.get("sub")
            if not user_id:
                logger.error("Token payload missing user ID")
                raise HTTPException(
                    status_code=401, detail="Token payload missing user ID"
                )
            print(user_id)
            # Fetch the user from the database
            async for db in get_db():
                user = await get_user_by_id(user_id, db=db)
                if not user:
                    logger.error(f"User with ID {user_id} not found")
                    raise HTTPException(status_code=401, detail="Invalid user")

            # Log successful authentication
            logger.info(f"User {user_id} authenticated successfully")
            request.state.user = user
        except jwt.ExpiredSignatureError:
            logger.warning(f"Expired token used by user: {payload.get('sub')}")
            return JSONResponse(
                status_code=401, content={"message": "Token has expired"}
            )
        except jwt.InvalidTokenError:
            logger.warning("Invalid token provided")
            return JSONResponse(status_code=401, content={"message": "Invalid token"})
        except Exception as e:
            logger.error(f"Error in JWT middleware: {str(e)}")
            return JSONResponse(status_code=500, content={"message": str(e)})

        return await call_next(request)
