import datetime
import re
from decimal import Decimal

import freezegun
import pytest
from aioresponses import aioresponses

from source.api.orders.handlers.create_order import _calculate_lots, _get_price_range, create_order_handler  # noqa
from source.api.orders.handlers.errors import TooLowRequestedVolumeError
from source.api.orders.schemas import CreateOrderResponse
from source.clients.binance.schemas.market.schemas import ExchangeInfoResponse
from source.clients.binance.schemas.wallet.schemas import APITradingStatus, APITradingStatusResponse
from source.enums import OrderSide, OrderType, SymbolStatus
from tests.unit.test_api.test_orders.utils import get_parametrize_for_calculate_lots_test


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


@pytest.mark.parametrize(
    'prices, min_quantity, step, volume, expected_lots',
    get_parametrize_for_calculate_lots_test(),
)
def test_calculate_lots(prices, min_quantity, step, volume, expected_lots):
    actual_lots = _calculate_lots(prices, min_quantity, step, volume)
    assert actual_lots == expected_lots


def test_calculate_lots_too_low_requested_volume_error():
    with pytest.raises(TooLowRequestedVolumeError):
        _calculate_lots(
            prices=[Decimal(12.50), Decimal(14.50), Decimal(10)],
            step=Decimal(1),
            min_quantity=Decimal(1),
            volume=Decimal(32),
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'latest_price, price_min, price_max, price_min_result, price_max_result', [
        (10, Decimal(5), Decimal(15), Decimal(5), Decimal(15)),
        (2, Decimal(5), Decimal(15), Decimal(5), Decimal(10)),
        (5, Decimal(2), Decimal(30), Decimal(2), Decimal(25)),
        (10, Decimal(1), Decimal(100), Decimal(2), Decimal(50)),
    ],
)
async def test_get_price_range(
        create_order_request,
        binance_client,
        binance_exchange_info_symbol,
        monkeypatch,
        latest_price,
        price_min,
        price_max,
        price_min_result,
        price_max_result,
):
    monkeypatch.setattr(
        target=binance_exchange_info_symbol,
        name='filters',
        value=[
            {
                'filterType': 'PERCENT_PRICE_BY_SIDE',
                'bidMultiplierUp': '5',
                'bidMultiplierDown': '0.2',
                'askMultiplierUp': '5',
                'askMultiplierDown': '0.2',
                'avgPriceMins': 5,
            },
        ],
    )
    monkeypatch.setattr(create_order_request, 'side', OrderSide.BUY)
    monkeypatch.setattr(create_order_request, 'priceMin', price_min)
    monkeypatch.setattr(create_order_request, 'priceMax', price_max)
    with aioresponses() as mock:
        mock.get(
            url=re.compile(r'.+/api/v3/ticker/price.+'),
            payload={
                'symbol': 'btcusdt',
                'price': latest_price,
            },
        )
        price_min_actual, price_max_actual = await _get_price_range(
            req=create_order_request,
            client=binance_client,
            symbol=binance_exchange_info_symbol,
        )
        assert price_min_actual == price_min_result
        assert price_max_actual == price_max_result
