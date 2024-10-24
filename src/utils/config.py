import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    MONGO_URI = os.getenv("MONGO_URI")
    MONGO_DATA_BASE = os.getenv("MONGO_DATA_BASE")
    BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
    BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")
    EXCHANGE_API_BASE_UR = os.getenv("EXCHANGE_API_BASE_URL")
    INFURA_ID = os.getenv("INFURA_ID")
    ALCHEMY_SOLANA = os.getenv("ALCHEMY_SOLANA")
    GETBLOCK_CARDANO = os.getenv("GETBLOCK_CARDANO")
    BLOCKFROST_CARDANO_KEY = os.getenv("BLOCKFROST_CARDANO_KEY")
    COIN_MARKETCAP_KEY = os.getenv("COIN_MARKETCAP_KEY")
    ALPHA_VANTAGE_KEY = os.getenv("ALPAH_VANTAGE_KEY")
    KRAKEN_API_KEY = os.getenv("KRAKEN_API_KEY")
    KRAKEN_PRIVATE_KEY = os.getenv("KRAKEN_PRIVATE_KEY")
    REDIS_URI = os.getenv("REDIS_URI")
    CONNECT_DB = os.getenv("CONNECT_DB") != "False"
    EXTRA_TAKER_FEE_PERCENTAGE = os.getenv("EXTRA_TAKER_FEE_PERCENTAGE")
    EXTRA_MAKER_FEE_PERCENTAGE = os.getenv("EXTRA_MAKER_FEE_PERCENTAGE")
    AUTH_SECURITY_KEY = os.getenv("AUTH_SECURITY_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
    ALGORITHM = os.getenv("ALGORITHM")
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
    FROM_EMAIL = os.getenv("FROM_EMAIL")
    BRAND_NAME = os.getenv("BRAND_NAME")
    CLICK_SEND_USER_NAME = os.getenv("CLICK_SEND_USER_NAME")
    CLICK_SEND_PASSWORD = os.getenv("CLICK_SEND_PASSWORD")
    DEFAULT_PASSWORD = os.getenv("DEFAULT_PASSWORD")
    REGISTRATION_EMAIL_TEMPLATE_ID = os.getenv("REGISTRATION_EMAIL_TEMPLATE_ID")
    LOGIN_EMAIL_TEMPLATE_ID = os.getenv("LOGIN_EMAIL_TEMPLATE_ID")
