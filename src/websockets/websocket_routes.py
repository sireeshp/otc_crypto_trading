# websocket_routes.py

from fastapi import APIRouter, WebSocket

from src.services.connect_exchange_service import get_exchange_by_exchange_name
from src.utils.app_utils import normalize_symbol
from src.utils.logger import setup_logger
from src.websockets.connection_manager import ConnectionManager

logger = setup_logger("websocket_routes", "logs/websocket_routes.log")
manager = ConnectionManager()
router = APIRouter()


@router.websocket("/ws/subscribe/{exchange_name}/{symbol}")
async def ws_subscribe_symbol(exchange_name: str, symbol: str, websocket: WebSocket):
    exchange = None
    ex_symbol = normalize_symbol(symbol)
    try:
        await manager.connect(websocket, ex_symbol, exchange_name)
        exchange = await get_exchange_by_exchange_name(exchange_name, ws=True)
        if exchange is None:
            logger.error(f"Exchange not found: {exchange_name}")
            return
        await exchange.load_markets()  # Load markets for the exchange
        while True:
            ticker = await exchange.watch_ticker(ex_symbol)
            logger.info(f"Received ticker data: {ticker}")
            await manager.send_ticker(
                ex_symbol, exchange_name, ticker
            )  # Broadcast to connected clients
    except Exception as e:
        logger.error(f"Error subscribing to {ex_symbol} on {exchange_name}: {e}")
    finally:
        if exchange:
            await exchange.close()
