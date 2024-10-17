from datetime import datetime, timedelta, timezone
from typing import Union

import jwt
from bson import ObjectId
from passlib.context import CryptContext
from pymongo.collection import Collection

from src.models.AuthModel import User
from src.utils.config import Config
from src.utils.logger import setup_logger
from src.utils.mongo_utils import get_otp_collection, get_users_collection

# Setup logger and password hashing context
logger = setup_logger("auth_service", "logs/auth_service.log")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = (
        datetime.utcnow(timezone.utc) + expires_delta
        if expires_delta
        else datetime.utcnow(timezone.utc) + timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire
    return jwt.encode(to_encode, Config.AUTH_SECURITY_KEY, algorithm=Config.ALGORITHM)


async def authenticate_email(email: str, password: str, db) -> Union[dict, None]:
    try:
        user_collection: Collection = get_users_collection(db)
        user: Union[User, None] = await user_collection({"email": email})
        if not user:
            raise ValueError("User not registered, please register.")

        is_valid = verify_password(password, user["password"])
        if not is_valid:
            raise ValueError("Invalid Password")

        user.pop("password", None)
        token_data = {"sub": str(user["_id"]), "email": user["email"]}
        token = await create_access_token(data=token_data)
        return {"token": token, "profile": user}
    except Exception as e:
        logger.error(f"Error during authentication: {e}")
        raise ValueError(e) from e


async def authenticate_otp(phone_number: str, otp: str, db) -> Union[dict, None]:
    try:
        otp_collection: Collection = get_otp_collection(db)
        user_collection: Collection = get_users_collection(db)

        user: Union[User, None] = await user_collection.find_one(
            {"phone_number": phone_number}
        )
        if not user:
            raise ValueError("User not registered, please register.")

        otp_record = await otp_collection.find_one(
            {"phone_number": phone_number, "otp": otp}
        )
        if not otp_record:
            raise ValueError("Invalid OTP.")
        if otp_record["expires_at"] < datetime.now(timezone.utc):
            raise ValueError("OTP has expired.")
        user.pop("password", None)
        token_data = {"sub": str(user["_id"]), "email": user["email"]}
        token = await create_access_token(data=token_data)
        await otp_collection.delete_one({"_id": otp_record["_id"]})
        return {"token": token, "profile": user}
    except Exception as e:
        logger.error(f"Error during authentication: {e}")
        raise ValueError(e) from e


async def get_user_by_id(id, db):
    if not id:
        raise ValueError("Id is required")
    try:
        # Ensure the id is a valid ObjectId
        object_id = ObjectId(id)
    except Exception as e:
        raise ValueError(f"Invalid ID format: {e}") from e
    user_collection: Collection = get_users_collection(db)
    user = user_collection.find_one({"_id": object_id})
    if user:
        user["_id"] = str(user["_id"])
        user.pop("password", None)
    return user
