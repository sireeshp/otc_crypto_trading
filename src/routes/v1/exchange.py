from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request

from src.models.ExchangeKeyModel import ExchangeKey
from src.services.connect_exchange_service import (
    add_exchange_key,
    bulk_add_exchange_key,
    get_user_exchange_keys,
)
from src.utils.mongo_utils import get_db

router = APIRouter()


@router.get("/user-exchange-keys")
async def load_user_exchange_keys(request: Request, db=Depends(get_db)):
    try:
        print(request.state.user)
        return await get_user_exchange_keys(request.state.user._id, db)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/add-exchange-key")
async def add_exchange_key_route(exchange_key: ExchangeKey, db=Depends(get_db)):
    try:
        return await add_exchange_key(exchange_key, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/bulk-add-exchange-key")
async def bulk_add_exchange_key_route(data: List[ExchangeKey], db=Depends(get_db)):
    try:
        return await bulk_add_exchange_key(data, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
