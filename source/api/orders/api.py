from fastapi import APIRouter
from starlette.responses import JSONResponse

from source.api.orders.handler import create_order_handler
from source.api.orders.schemas import CreateOrderRequest, CreateOrderResponse
from source.clients.binance.errors import BinanceHttpError

orders_router = APIRouter(prefix='/order')


@orders_router.post(path='/create', response_model=CreateOrderResponse)
async def create_order(request: CreateOrderRequest):
    if request.priceMin > request.priceMax:
        response = CreateOrderResponse(
            success=False,
            error='priceMax cannot be less than priceMin',
        )
        return JSONResponse(status_code=400, content=response.dict())
    try:
        return await create_order_handler(request)
    except BinanceHttpError as error:
        return CreateOrderResponse(success=False, error=error.msg)
