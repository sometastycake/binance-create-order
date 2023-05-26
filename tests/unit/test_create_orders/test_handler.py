import datetime
import re
from decimal import Decimal
from typing import Tuple

import freezegun
import pytest
from aioresponses import aioresponses

from source.api.orders.handlers.create_order import create_order_handler
from source.api.orders.schemas import CreateOrderRequest, CreateOrderResponse
from source.clients.binance.schemas.market.schemas import ExchangeInfoResponse, Symbol
from source.clients.binance.schemas.wallet.schemas import APITradingStatus, APITradingStatusResponse
from source.enums import OrderSide, OrderType, SymbolStatus


def get_exchange_info_payload(
        symbol: str = 'BTCUSDT',
        spot_trading_allowed: bool = True,
        symbol_status: SymbolStatus = SymbolStatus.TRADING,
        order_types: Tuple = (OrderType.LIMIT, ),
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
                filters=[],
            ),
        ],
    )


def mock_exchange_info_response(mock: aioresponses, payload: ExchangeInfoResponse):
    mock.get(url=re.compile(r'.+exchangeInfo.+$'), body=payload.json())


def mock_api_trading_status_response(mock: aioresponses) -> None:
    response = APITradingStatusResponse(
        data=APITradingStatus(
            isLocked=False,
        )
    )
    mock.get(url=re.compile(r'.+apiTradingStatus.+$'), body=response.json())


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'payload, error', [
        (get_exchange_info_payload(order_types=(OrderType.STOP_LOSS, )), 'Limit order disabled'),
        (get_exchange_info_payload(symbol_status=SymbolStatus.HALT), 'Wrong trading symbol status'),
        (get_exchange_info_payload(spot_trading_allowed=False), 'Spot trading disabled'),
        (get_exchange_info_payload(symbol='BTCUST'), 'Not found trading symbol'),
    ],
)
@freezegun.freeze_time(datetime.datetime(2023, 1, 1, 10, 0, 0, 0))
async def test_create_order_handler_error(payload, error):
    request = CreateOrderRequest(
        symbol='btcusdt',
        volume=Decimal(10),
        number=5,
        amountDif=Decimal(5),
        side=OrderSide.BUY,
        priceMin=Decimal(2),
        priceMax=Decimal(5),
    )
    with aioresponses() as mock:
        mock_exchange_info_response(mock, payload)
        mock_api_trading_status_response(mock)
        response = await create_order_handler(request)
    assert response == CreateOrderResponse(success=False, error=error)
