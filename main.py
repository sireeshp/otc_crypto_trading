from src.data.fetch_data import fetch_historical_data, fetch_ticker

def main():
    ticker_data = fetch_ticker()
    print(ticker_data)
    
if __name__ == "__main__":
    main()

