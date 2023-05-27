import asyncio
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from source.api.app import app
from source.api.orders.schemas import CreateOrderRequest
from source.clients.binance.client import BinanceClient
from source.clients.binance.schemas.market.schemas import Symbol
from source.enums import OrderSide, OrderType, SymbolStatus


@pytest.fixture(scope='session')
def binance_client():
    client = BinanceClient()
    try:
        yield client
    finally:
        asyncio.get_event_loop().run_until_complete(client.connector.close())


@pytest.fixture(scope='session')
def fast_api_app():
    return TestClient(app)


@pytest.fixture(scope='function')
def binance_exchange_info_symbol():
    return Symbol(
        symbol='BTCUSDT',
        status=SymbolStatus.TRADING,
        orderTypes=[OrderType.LIMIT],
        quoteOrderQtyMarketAllowed=False,
        isSpotTradingAllowed=True,
        permissions=['SPOT'],
        filters=[],
    )


@pytest.fixture(scope='function')
def create_order_request():
    return CreateOrderRequest(
        symbol='btcusdt',
        volume=Decimal(10),
        number=5,
        amountDif=Decimal(5),
        side=OrderSide.BUY,
        priceMin=Decimal(2),
        priceMax=Decimal(5),
    )
