import random
from datetime import datetime, timedelta, timezone
from typing import List, Union

import jwt
from bson import ObjectId
from passlib.context import CryptContext
from pymongo.collection import Collection
from pymongo.errors import BulkWriteError

from src.models.AuthModel import CryptoWallet, KycData, Transaction, User
from src.models.EmailModel import EmailModel
from src.services.email_service import send_email
from src.services.sms_service import send_sms
from src.utils.config import Config
from src.utils.logger import setup_logger
from src.utils.mongo_utils import get_otp_collection, get_users_collection

# Setup logger and password hashing context
logger = setup_logger("auth_service", "logs/auth_service.log")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    print(hashed_password)
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def create_access_token(data: dict):
    to_encode = data.copy()
    expires_delta = timedelta(minutes=int(Config.ACCESS_TOKEN_EXPIRE_MINUTES))
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode["exp"] = expire
    return jwt.encode(to_encode, Config.AUTH_SECURITY_KEY, algorithm=Config.ALGORITHM)


async def find_user(email: str, phone_number: str, db):
    user_collection = get_users_collection(db=db)
    return await user_collection.find_one(
        {
            "$or": [
                {"email": email},  # if searching by email
                {"phone_number": phone_number},  # if searching by phone number
            ]
        }
    )


def get_user_vm(user: User):
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone_number": user.phone_number,
        "user_type": user.user_type,
        "about": user.about,
        "avatar_url": user.avatar_url,
        "user_tier": user.user_tier,
        "two_factor_enabled": user.two_factor_enabled,
        "two_factor_method": user.two_factor_method,
        "login_attempts": user.login_attempts,
        "last_login": user.last_login,
        "ai_trading_enabled": user.ai_trading_enabled,
        "trading_limits": user.trading_limits,
        "legal_compliance": user.legal_compliance,
        "trading_products": user.trading_products,
        "roles": user.roles,
        "data_store_preference": user.data_store_preference,
    }


async def delete_user(user_id: str, db):
    user_collection = get_users_collection(db=db)
    return await user_collection.delete_one({"_id": ObjectId(user_id)})


async def add_user(user: User, db):
    try:
        db_user = await find_user(user.email, user.phone_number, db)
        if db_user is not None:
            raise ValueError("User already exist")
        if user.password is None:
            user.password = Config.DEFAULT_PASSWORD
        user.password = get_password_hash(user.password)
        user_collection = get_users_collection(db=db)
        user_data = user.model_dump()
        response = await user_collection.insert_one(user_data)
        user.id = str(response.inserted_id)
        profile = get_user_vm(user)
        token_data = {"sub": profile["id"], "email": profile["email"]}
        token = await create_access_token(data=token_data)
        return {"token": token, "profile": profile}
    except Exception as e:
        print(e)
        logger.error(f"add_user: {str(e)}")
        raise ValueError(e) from e


async def add_user_collection(users: List[User], db):
    try:
        exist = []
        not_exist = []
        for user in users:
            db_user = find_user(user.email, user.phone_number, db)
            if db_user is not None:
                exist.append(user)
            else:
                not_exist.append(user)
                if user.password is None:
                    user.password = Config.DEFAULT_PASSWORD
                user.password = get_password_hash(user.password)
        user_collection = get_users_collection(db=db)
        response = await user_collection.insert_many(not_exist)
        if response.acknowledged:
            inserted_count = len(response.inserted_ids)
            return {
                "status": "success",
                "inserted_count": inserted_count,
                "failed": exist,
            }
        else:
            raise ValueError("Insert operation not acknowledged by the server")
    except BulkWriteError as bwe:
        # Handle any bulk write errors
        logger.error(f"Bulk write error occurred: {bwe.details}")
        raise ValueError({"status": "failed", "error": bwe.details}) from bwe
    except Exception as e:
        # Catch any other exceptions
        logger.error(f"An error occurred during insert_many: {str(e)}")
        raise ValueError({"status": "failed", "error": str(e)}) from e


async def update_user(user_id: str, update_data: dict, db) -> User:
    user_collection: Collection = get_users_collection(db)
    return await user_collection.update_one(
        {"_id": ObjectId(user_id)}, {"$set": update_data}
    )


async def add_crypto_wallet(user_id: str, wallet_data: CryptoWallet, db) -> User:
    try:
        user_collection: Collection = get_users_collection(db)
        return await user_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$push": {"crypto_wallets": wallet_data.model_dump()}},
        )
    except Exception as e:
        logger.error(f"Failed to add crypto wallet: {e}")
        raise ValueError(e) from e


async def add_transaction(user_id: str, transaction_data: Transaction, db) -> User:
    try:
        user_collection: Collection = get_users_collection(db)
        return await user_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$push": {"transaction_history": transaction_data.model_dump()}},
        )
    except Exception as e:
        logger.error(f"Failed to add transaction: {e}")
        raise ValueError(e) from e


async def update_kyc_data(user_id: str, kyc_data: KycData, db) -> User:
    try:
        user_collection: Collection = get_users_collection(db)
        return await user_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$push": {"kyc_data": kyc_data.model_dump()}},
        )
    except Exception as e:
        logger.error(f"Failed to add transaction: {e}")
        raise ValueError(e) from e


async def enable_two_factor(user_id: str, method: str, db) -> User:
    try:
        user_collection: Collection = get_users_collection(db)
        return await user_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"two_factor_enabled": True, "two_factor_method": method}},
        )
    except Exception as e:
        logger.error(f"Failed to add transaction: {e}")
        raise ValueError(e) from e


async def disable_two_factor(user_id: str, db) -> User:
    try:
        user_collection: Collection = get_users_collection(db)
        return await user_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"two_factor_enabled": True, "two_factor_method": None}},
        )
    except Exception as e:
        logger.error(f"Failed to add transaction: {e}")
        raise ValueError(e) from e


async def authenticate_email(email: str, password: str, db) -> Union[dict, None]:
    try:
        user_collection: Collection = get_users_collection(db)
        response: Union[User, None] = await user_collection.find_one({"email": email})
        if not response:
            raise ValueError("User not registered, please register.")

        is_valid = verify_password(password, response["password"])
        if not is_valid:
            raise ValueError("Invalid Password")
        response["id"] = str(response["_id"])
        profile = get_user_vm(User(**response))
        token_data = {"sub": profile["id"], "email": profile["email"]}
        token = await create_access_token(data=token_data)
        return {"token": token, "profile": profile}
    except Exception as e:
        print(e)
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


async def send_otp(user_name: str, db):
    """
    Generates and sends a One-Time Password (OTP) to the specified user via email or SMS.

    This asynchronous function checks if the user is registered and generates a 6-digit OTP,
    which is then sent to the user through their preferred communication method.
    It handles both email and phone number formats for user identification and logs
    the success or failure of the OTP sending process.

    Args:
        user_name (str): The user's phone number or email address.
        db: The database connection for user and OTP management.

    Returns:
        dict: A message indicating the success of the OTP sending process.

    Raises:
        ValueError: If the user name is not provided, if the user is not registered, or if an error occurs during OTP generation or sending.
    """

    try:
        if not user_name:
            raise ValueError("Phone Number or Email is required")

        user_collection: Collection = get_users_collection(db)
        is_email = "@" in user_name
        # Query user based on email or phone
        user: Union[User, None] = await user_collection.find_one(
            {"email": user_name} if is_email else {"phone": user_name}
        )
        if not user:
            raise ValueError("User not registered, please register.")

        # Generate a 6-digit OTP
        otp = random.randint(100000, 999999)

        otp_collection: Collection = get_otp_collection(db)
        otp_model = {"user_name": user_name, "otp": otp}

        # Store or update the OTP in the collection
        await otp_collection.update_one(
            {"user_name": user_name}, {"$set": otp_model}, upsert=True
        )

        if is_email:
            # Prepare email contents
            email_subject = f"Your OTP Code for {Config.BRAND_NAME}"

            plain_text_content = (
                f"Dear {user['name']},\n\n"
                f"Your One-Time Password (OTP) for accessing {Config.BRAND_NAME} is: {otp}.\n\n"
                "For security reasons, please do not share this code with anyone.\n"
                "If you did not request this code, please ignore this email.\n\n"
                "Best regards,\n"
                f"The {Config.BRAND_NAME} Team"
            )

            html_content = (
                f"<html><body>"
                f"<p>Dear {user['name']},</p>"
                f"<p>Your One-Time Password (OTP) for accessing <strong>{Config.BRAND_NAME}</strong> is:</p>"
                f"<h2 style='color: #2e6c80;'>{otp}</h2>"
                f"<p>Please use this code to complete your login process. For security reasons, do not share this code with anyone.</p>"
                f"<p>If you did not request this code, please ignore this email.</p>"
                f"<p>Best regards,</p>"
                f"<p>The <strong>{Config.BRAND_NAME}</strong> Team</p>"
                f"</body></html>"
            )

            # Send email asynchronously
            await send_email(
                EmailModel(
                    from_email=user["email"],
                    subject=email_subject,
                    plain_text_content=plain_text_content,
                    html_content=html_content,
                )
            )
        else:
            # Send SMS asynchronously
            await send_sms(
                user["phone"],
                message=f"{otp} is your One-Time Password (OTP) for accessing {Config.BRAND_NAME}",
            )

        logger.info(f"OTP sent successfully to {user_name}")
        return {"message": "OTP sent successfully"}

    except Exception as e:
        logger.error(f"Error during OTP generation: {e}")
        raise ValueError(f"Failed to send OTP: {e}") from e


async def get_user_by_id(id, db):
    if not id:
        raise ValueError("Id is required")
    try:
        # Ensure the id is a valid ObjectId
        object_id = ObjectId(id)
    except Exception as e:
        raise ValueError(f"Invalid ID format: {e}") from e
    user_collection: Collection = get_users_collection(db)
    user = await user_collection.find_one({"_id": object_id})
    if user:
        user["_id"] = str(user["_id"])
        user.pop("password", None)
    return user
