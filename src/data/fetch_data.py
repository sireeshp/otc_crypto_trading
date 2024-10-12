import ccxt
from src.utils.config import Config

# Initialize the exchange using environment variables
def  initialize_exchange():
    exchange = ccxt.kraken({
        'apiKey': Config.KRAKEN_API_KEY,
        'secret': Config.KRAKEN_PRIVATE_KEY,
    })
    return exchange

# Fetch historical data
def fetch_historical_data(symbol='BTC/USD',timeframe='1h',since=None):
    exchange = initialize_exchange()
    ohlcv = exchange.fetch_ohlcv(symbol,timeframe,since=since)
    return ohlcv


# Fetch real-time ticker data
def fetch_ticker(symbol = 'BTC/USD'):
    exchange = initialize_exchange()
    ticker = exchange.fetch_ticker(symbol)
    return ticker

if __name__ == "__main__":
    historical_data = fetch_historical_data()
    print(historical_data)
    ticker_data=fetch_ticker()
    print(ticker_data)