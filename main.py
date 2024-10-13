import asyncio
from src.data.fetch_data import price_engine

async def main():
    ticker_data = await price_engine()
    print(ticker_data)
    
if __name__ == "__main__":
    asyncio.run(main())

