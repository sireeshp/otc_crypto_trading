from typing import Dict, List

from fastapi import WebSocket

from src.utils.logger import setup_logger

logger = setup_logger("connection_manager", "logs/connection_manager.log")


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, symbol: str, exchange_name: str):
        await websocket.accept()
        key = f"{exchange_name}:{symbol}"
        if key not in self.active_connections:
            self.active_connections[key] = []
        self.active_connections[key].append(websocket)
        logger.info(f"Client subscribed to {key}")

    async def disconnect(self, websocket: WebSocket, symbol: str, exchange_name: str):
        key = f"{exchange_name}:{symbol}"
        self.active_connections[key].remove(websocket)
        if len(self.active_connections[key]) == 0:
            del self.active_connections[key]
        logger.info(f"Client unsubscribed from {key}")

    async def send_ticker(self, symbol: str, exchange_name: str, ticker_data: dict):
        key = f"{exchange_name}:{symbol}"
        if key in self.active_connections:
            for connection in self.active_connections[key]:
                await connection.send_json(ticker_data)
                logger.info(f"Sent ticker data to client for {key}")

    async def broadcast(self, message: str):
        for symbol_connections in self.active_connections.values():
            for connection in symbol_connections:
                await connection.send_text(message)
