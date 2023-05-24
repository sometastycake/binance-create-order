from fastapi import APIRouter

from source.api.orders.handler import create_order_handler
from source.api.orders.schemas import CreateOrderRequest, CreateOrderResponse
from source.clients.binance.errors import BinanceHttpError

orders_router = APIRouter(prefix='/order')


@orders_router.post(path='/create', response_model=CreateOrderResponse)
async def create_order(request: CreateOrderRequest):
    try:
        return await create_order_handler(request)
    except BinanceHttpError as error:
        return CreateOrderResponse(success=False, error=error.msg)
