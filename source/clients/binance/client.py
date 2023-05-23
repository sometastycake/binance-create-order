from decimal import Decimal
from typing import Dict, Optional

from source.clients.binance.connector import BinanceConnectorAbstract, DefaultBinanceConnector
from source.clients.binance.schemas.order.schemas import CheckOrderStatusRequest, NewOrderRequest
from source.enums import OrderSide, OrderType


class BinanceClient:

    def __init__(self, connector: Optional[BinanceConnectorAbstract] = None):
        self._connector = connector or DefaultBinanceConnector()

    async def create_new_order(
            self,
            symbol: str,
            side: OrderSide,
            order_type: OrderType,
            quantity: Optional[Decimal] = None,
            quote_order_qty: Optional[Decimal] = None,
            price: Optional[Decimal] = None,
            new_client_order_id: Optional[str] = None,
    ) -> Dict:
        request = NewOrderRequest(
            symbol=symbol,
            side=side,
            type=order_type,
            quantity=quantity,
            quoteOrderQty=quote_order_qty,
            price=price,
            newClientOrderId=new_client_order_id,
        )
        request.sign()
        return await self._connector.request('/api/v3/order', 'POST', body=request.to_query())

    async def check_order_status(
            self,
            symbol: str,
            order_id: Optional[int] = None,
            orig_client_order_id: Optional[str] = None,
    ) -> Dict:
        request = CheckOrderStatusRequest(
            symbol=symbol,
            orderId=order_id,
            origClientOrderId=orig_client_order_id,
        )
        request.sign()
        params = request.dict(exclude_none=True)
        return await self._connector.request('/api/v3/order', 'GET', params=params)
