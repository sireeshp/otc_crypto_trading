from unittest.mock import AsyncMock, patch

import pytest

from src.data.exchange_keys import get_exchange_keys
from src.models.ExchangeKey import ExchangeKey
from src.utils.config import Config


@pytest.mark.asyncio
async def test_get_exchange_keys_success():
    mock_api_keys = [
        {
            "api_key": "test_key_1",
            "api_secret": "test_secret_1",
            "exchange_name": "Kraken",
            "passphrase": None,
        },
        {
            "api_key": "test_key_2",
            "api_secret": "test_secret_2",
            "exchange_name": "Binance",
            "passphrase": "test_passphrase",
        },
    ]
    with patch(
        "src.data.exchange_keys.db.api_keys.find",
        AsyncMock(return_value=mock_api_keys),
    ):
        result = await get_exchange_keys()
        assert len(result) == 2
        assert isinstance(result[0], ExchangeKey)
        assert result[0].exchange_name == "Kraken"
        assert result[1].exchange_name == "Binance"


@pytest.mark.asyncio
async def test_get_exchange_keys_failure():
    with patch(
        "src.data.exchange_keys.server_info",
        side_effect=ConnectionError("MongoDB connection failed"),
    ):
        result = await get_exchange_keys()
        assert len(result) == 1
        assert result[0].exchange_name == "Kraken"
        assert result[0].api_key == Config.KRAKEN_API_KEY
        assert result[0].api_secret == Config.KRAKEN_PRIVATE_KEY
