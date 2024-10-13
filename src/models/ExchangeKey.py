from dataclasses import dataclass

@dataclass
class ExchangeKey:
    api_key:str
    api_secret:str
    exchange_name:str