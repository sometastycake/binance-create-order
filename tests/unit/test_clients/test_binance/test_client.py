import datetime
import re
from decimal import Decimal

import freezegun
import pytest
from aioresponses import aioresponses

from source.clients.binance.errors import BinanceHttpError
from source.clients.binance.schemas.market.schemas import ExchangeInfoResponse, LatestPriceResponse, Symbol
from source.clients.binance.schemas.order.schemas import NewOrderRequest, NewOrderResponse
from source.clients.binance.schemas.wallet.schemas import APITradingStatusResponse
from source.clients.binance.signature import BaseSignature
from source.config import config
from source.enums import OrderSide, OrderType, SymbolStatus, TimeInForce


@pytest.mark.asyncio
async def test_exchange_info(binance_client):
    symbol = {
        'symbol': 'BTCUSDT',
        'status': 'TRADING',
        'orderTypes': ['LIMIT', 'MARKET'],
        'quoteOrderQtyMarketAllowed': False,
        'isSpotTradingAllowed': True,
        'permissions': ['SPOT'],
        'filters': [],
    }
    with aioresponses() as mock:
        mock.get(
            url=re.compile(r'.+exchangeInfo.+$'),
            payload={'symbols': [symbol]},
        )
        response = await binance_client.exchange_info('btcusdt')
    assert response == ExchangeInfoResponse(
        symbols=[
            Symbol(
                symbol='BTCUSDT',
                status=SymbolStatus.TRADING,
                orderTypes=[OrderType.LIMIT, OrderType.MARKET],
                quoteOrderQtyMarketAllowed=False,
                isSpotTradingAllowed=True,
                permissions=['SPOT'],
                filters=[],
            ),
        ],
    )


@pytest.mark.asyncio
async def test_exchange_info_error(binance_client):
    payload = {
        'code': -1121,
        'msg': 'Invalid symbol.',
    }
    with aioresponses() as mock:
        mock.get(
            url=re.compile(r'.+exchangeInfo.+$'),
            payload=payload,
            status=400,
        )
        with pytest.raises(BinanceHttpError) as error:
            await binance_client.exchange_info('btcusdt')
    assert error.value.code == -1121
    assert error.value.msg == 'Invalid symbol.'


@pytest.mark.asyncio
@freezegun.freeze_time(datetime.datetime(2023, 1, 1, 10, 0, 0, 0))
async def test_get_api_trading_status(binance_client, monkeypatch):
    with aioresponses() as mock:
        mock.get(
            url=re.compile(r'.+apiTradingStatus.+$'),
            payload={
                'data': {'isLocked': True},
            },
        )
        params = BaseSignature()
        monkeypatch.setattr(config, 'BINANCE_SECRET_KEY', 'SECRET')
        response = await binance_client.get_api_trading_status(params)
        assert params.recvWindow == 5000
        assert params.signature == '222e7d13bcb8e8acb1ca6a716c864f1965e74807b9770bd4b5ed50057c256bef'
        assert isinstance(response, APITradingStatusResponse)
        assert response.data.isLocked is True


@pytest.mark.asyncio
async def test_get_api_trading_status_error(binance_client):
    with aioresponses() as mock:
        mock.get(
            url=re.compile(r'.+apiTradingStatus.+$'),
            payload={
                'code': -1,
                'msg': 'Invalid IP key or permissions',
            },
            status=400,
        )
        with pytest.raises(BinanceHttpError) as error:
            await binance_client.get_api_trading_status()
        assert error.value.code == -1
        assert error.value.msg == 'Invalid IP key or permissions'


@pytest.mark.asyncio
async def test_get_latest_price(binance_client):
    with aioresponses() as mock:
        mock.get(
            url=re.compile(r'.+ticker/price.+$'),
            payload={
                'symbol': 'btcusdt',
                'price': 2,
            },
        )
        response = await binance_client.get_latest_price('btcusdt')
        assert isinstance(response, LatestPriceResponse)
        assert response.symbol == 'btcusdt'
        assert response.price == Decimal(2)


@pytest.mark.asyncio
async def test_get_latest_price_error(binance_client):
    with aioresponses() as mock:
        mock.get(
            url=re.compile(r'.+ticker/price.+$'),
            payload={
                'code': -1121,
                'msg': 'Invalid symbol.',
            },
            status=400,
        )
        with pytest.raises(BinanceHttpError) as error:
            await binance_client.get_latest_price('btcusdt')
        assert error.value.code == -1121
        assert error.value.msg == 'Invalid symbol.'


@pytest.mark.asyncio
@freezegun.freeze_time(datetime.datetime(2023, 1, 1, 10, 0, 0, 0))
async def test_create_new_order(binance_client, monkeypatch):
    payload = {
        'symbol': 'btcusdt',
        'orderId': 1,
        'transactTime': 2,
        'price': 5,
        'status': 'FILLED',
        'timeInForce': 'GTC',
        'type': OrderType.LIMIT.value,
        'side': OrderSide.SELL.value,
    }
    with aioresponses() as mock:
        mock.post(
            url=re.compile(r'.+/v3/order'),
            payload=payload,
        )
        monkeypatch.setattr(config, 'BINANCE_SECRET_KEY', 'SECRET')
        request = NewOrderRequest(
            symbol='btcusdt',
            side=OrderSide.SELL,
            type=OrderType.LIMIT,
            quantity=Decimal(2),
            price=Decimal(5),
        )
        response = await binance_client.create_new_order(request)
        assert request.recvWindow == 5000
        assert request.signature == '8142f383586a2b172d740c3dd946a297c549b784079492ab46c45b959db7679c'
        assert response == NewOrderResponse(
            symbol='btcusdt',
            orderId=1,
            transactTime=2,
            price=Decimal(5),
            status='FILLED',
            timeInForce=TimeInForce.GTC,
            type=OrderType.LIMIT,
            side=OrderSide.SELL,
        )
