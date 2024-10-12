import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BINANCE_API_KEY=os.getenv('BINANCE_API_KEY')
    BINANCE_SECRET_KEY=os.getenv('BINANCE_SECRET_KEY')
    EXCHANGE_API_BASE_UR=os.getenv('EXCHANGE_API_BASE_URL')
    INFURA_ID = os.getenv("INFURA_ID")
    ALCHEMY_SOLANA = os.getenv("ALCHEMY_SOLANA")
    GETBLOCK_CARDANO = os.getenv("GETBLOCK_CARDANO")
    BLOCKFROST_CARDANO_KEY = os.getenv("BLOCKFROST_CARDANO_KEY")
    COIN_MARKETCAP_KEY = os.getenv("COIN_MARKETCAP_KEY")
    ALPHA_VANTAGE_KEY = os.getenv("ALPAH_VANTAGE_KEY")
    KRAKEN_API_KEY = os.getenv("KRAKEN_API_KEY")
    KRAKEN_PRIVATE_KEY = os.getenv("KRAKEN_PRIVATE_KEY")
