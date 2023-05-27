from fastapi import APIRouter
from starlette.responses import JSONResponse

from source.api.orders.handlers.create_order import create_order_handler
from source.api.orders.schemas import CreateOrderRequest, CreateOrderResponse
from source.clients.binance.client import BinanceClient
from source.clients.binance.errors import BinanceHttpError
from source.logger import logger

orders_router = APIRouter(prefix='/order')


@orders_router.post(path='/create', response_model=CreateOrderResponse)
async def create_order(request: CreateOrderRequest):
    logger.info('Request %s' % request)
    # TODO в логировании нужен некоторый trace_id, по которому удобно собирать логи одного реквеста
    if request.priceMin > request.priceMax:
        response = CreateOrderResponse(
            success=False,
            error='priceMax cannot be less than priceMin',
        )
        return JSONResponse(status_code=400, content=response.dict())
    try:
        async with BinanceClient() as client:
            return await create_order_handler(request, client)
    except BinanceHttpError as error:
        return CreateOrderResponse(success=False, error=error.msg)
