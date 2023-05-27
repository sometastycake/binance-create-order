import datetime
import re

import freezegun
import pytest
from aioresponses import aioresponses

from source.api.orders.handlers.create_order import create_order_handler
from source.api.orders.schemas import CreateOrderResponse
from source.clients.binance.schemas.market.schemas import ExchangeInfoResponse
from source.clients.binance.schemas.wallet.schemas import APITradingStatus, APITradingStatusResponse
from source.enums import OrderType, SymbolStatus


def mock_exchange_info_response(mock: aioresponses, payload: ExchangeInfoResponse) -> None:
    mock.get(url=re.compile(r'.+exchangeInfo.+$'), body=payload.json())


def mock_api_trading_status_response(mock: aioresponses, status: bool = False) -> None:
    response = APITradingStatusResponse(
        data=APITradingStatus(
            isLocked=status,
        ),
    )
    mock.get(url=re.compile(r'.+apiTradingStatus.+$'), body=response.json())


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'name, value, error', [
        ('orderTypes', [OrderType.STOP_LOSS], 'Limit order disabled'),
        ('status', SymbolStatus.HALT, 'Wrong trading symbol status'),
        ('isSpotTradingAllowed', False, 'Spot trading disabled'),
        ('symbol', 'BTCUST', 'Not found trading symbol'),
    ],
)
@freezegun.freeze_time(datetime.datetime(2023, 1, 1, 10, 0, 0, 0))
async def test_create_order_handler_exchange_info_error(
        name, value, error, binance_client, binance_exchange_info_symbol, create_order_request,
):
    setattr(binance_exchange_info_symbol, name, value)
    with aioresponses() as mock:
        mock_exchange_info_response(mock, ExchangeInfoResponse(symbols=[binance_exchange_info_symbol]))
        mock_api_trading_status_response(mock)
        response = await create_order_handler(create_order_request, binance_client)
    assert response == CreateOrderResponse(success=False, error=error)


@pytest.mark.asyncio
async def test_create_order_handler_api_status_disabled(binance_client, create_order_request):
    with aioresponses() as mock:
        mock_api_trading_status_response(mock, True)
        response = await create_order_handler(create_order_request, binance_client)
    assert response == CreateOrderResponse(
        success=False,
        error='API trading function is locked',
    )
