from typing import Optional

from pydantic import BaseModel


class ExchangeKey(BaseModel):
    api_key: str
    api_secret: str
    exchange_name: str
    user_id: Optional[str]
