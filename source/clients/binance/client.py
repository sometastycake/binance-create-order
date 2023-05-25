from decimal import Decimal
from typing import Dict, Optional

from source.clients.binance.connector import BinanceConnectorAbstract, DefaultBinanceConnector
from source.clients.binance.schemas.market.schemas import ExchangeInfoResponse
from source.clients.binance.schemas.order.schemas import CheckOrderStatusRequest, NewOrderRequest, NewOrderResponse
from source.enums import OrderSide, OrderType, TimeInForce


class BinanceClient:

    def __init__(self, connector: Optional[BinanceConnectorAbstract] = None, **kwargs):
        self._connector = connector or DefaultBinanceConnector(**kwargs)

    async def __aenter__(self) -> 'BinanceClient':
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._connector.close()

    async def exchange_info(self, symbol: str) -> ExchangeInfoResponse:
        return await self._connector.request(
            path='/api/v3/exchangeInfo',
            method='GET',
            params={
                'symbol': symbol.upper(),
            },
            response_model=ExchangeInfoResponse,
        )

    async def create_new_order(
            self,
            symbol: str,
            side: OrderSide,
            order_type: OrderType,
            quantity: Optional[Decimal] = None,
            quote_order_qty: Optional[Decimal] = None,
            price: Optional[Decimal] = None,
            new_client_order_id: Optional[str] = None,
            time_in_force: Optional[TimeInForce] = None,
    ) -> NewOrderResponse:
        request = NewOrderRequest(
            symbol=symbol,
            side=side,
            type=order_type,
            quantity=quantity,
            quoteOrderQty=quote_order_qty,
            price=price,
            newClientOrderId=new_client_order_id,
            timeInForce=time_in_force,
        )
        request.sign()
        return await self._connector.request(
            path='/api/v3/order',
            method='POST',
            body=request.to_query(),
            response_model=NewOrderResponse,
        )

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
