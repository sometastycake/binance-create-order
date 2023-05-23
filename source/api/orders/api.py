from fastapi import APIRouter

from source.api.orders.schemas import CreateOrderRequest

orders_router = APIRouter(prefix='/order')


@orders_router.post(path='/create')
async def create_order(request: CreateOrderRequest):
    return {'success': True}
