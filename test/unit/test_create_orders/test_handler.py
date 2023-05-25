from decimal import Decimal
from typing import Tuple

import pytest
from aioresponses import aioresponses
from yarl import URL

from source.api.orders.handler import create_order_handler
from source.api.orders.schemas import CreateOrderRequest, CreateOrderResponse
from source.clients.binance.schemas.market.schemas import ExchangeInfoResponse, Symbol
from source.config import config
from source.enums import OrderSide, OrderType, SymbolStatus


def get_exchange_info_payload(
        symbol: str = 'BTCUSDT',
        spot_trading_allowed: bool = True,
        symbol_status: SymbolStatus = SymbolStatus.TRADING,
        order_types: Tuple = (OrderType.LIMIT, )
) -> ExchangeInfoResponse:
    return ExchangeInfoResponse(
        symbols=[
            Symbol(
                symbol=symbol,
                status=symbol_status,
                orderTypes=list(order_types),
                quoteOrderQtyMarketAllowed=False,
                isSpotTradingAllowed=spot_trading_allowed,
                permissions=['SPOT'],
                filters=[]
            )
        ]
    )


def create_order_request() -> CreateOrderRequest:
    return CreateOrderRequest(
        symbol='btcusdt',
        volume=Decimal(10),
        number=5,
        amountDif=Decimal(5),
        side=OrderSide.BUY,
        priceMin=Decimal(2),
        priceMax=Decimal(5),
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'payload, error', [
        (get_exchange_info_payload(order_types=(OrderType.STOP_LOSS, )), 'Limit order disabled'),
        (get_exchange_info_payload(symbol_status=SymbolStatus.HALT), 'Wrong trading symbol status'),
        (get_exchange_info_payload(spot_trading_allowed=False), 'Spot trading disabled'),
        (get_exchange_info_payload(symbol='BTCUST'), 'Not found trading symbol')
    ]
)
async def test_create_order_handler_error(payload, error):
    url = config.get_binance_api('/api/v3/exchangeInfo')
    request = create_order_request()
    with aioresponses() as mock:
        mock.get(url=URL(url).with_query({'symbol': 'BTCUSDT'}), body=payload.json())
        response = await create_order_handler(request)
    assert response == CreateOrderResponse(success=False, error=error)
