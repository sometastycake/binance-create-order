import pytest
from aioresponses import aioresponses
from yarl import URL

from source.clients.binance.errors import BinanceHttpError
from source.clients.binance.schemas.market.schemas import ExchangeInfoResponse, Symbol
from source.config import config
from source.enums import OrderType, SymbolStatus


@pytest.mark.asyncio
async def test_exchange_info(binance_client):
    url = config.get_binance_api('/api/v3/exchangeInfo')
    payload = {
        'symbols': [
            {
                'symbol': 'BTCUSDT',
                'status': 'TRADING',
                'orderTypes': [
                    'LIMIT',
                    'MARKET',
                ],
                'quoteOrderQtyMarketAllowed': False,
                'isSpotTradingAllowed': True,
                'permissions': [
                    'SPOT',
                ],
                'filters': [],
            },
        ],
    }
    with aioresponses() as mock:
        mock.get(
            url=URL(url).with_query({'symbol': 'BTCUSDT'}),
            payload=payload,
        )
        response = await binance_client.exchange_info('btcusdt')
    assert isinstance(response, ExchangeInfoResponse)
    assert response.symbols == [
        Symbol(
            symbol='BTCUSDT',
            status=SymbolStatus.TRADING,
            orderTypes=[
                OrderType.LIMIT,
                OrderType.MARKET,
            ],
            quoteOrderQtyMarketAllowed=False,
            isSpotTradingAllowed=True,
            permissions=['SPOT'],
            filters=[],
        ),
    ]


@pytest.mark.asyncio
async def test_exchange_info_error(binance_client):
    url = config.get_binance_api('/api/v3/exchangeInfo')
    payload = {
        'code': -1121,
        'msg': 'Invalid symbol.',
    }
    with aioresponses() as mock:
        mock.get(
            url=URL(url).with_query({'symbol': 'BTCUSDT'}),
            payload=payload,
            status=400,
        )
        with pytest.raises(BinanceHttpError) as error:
            await binance_client.exchange_info('btcusdt')
    assert error.value.code == -1121
    assert error.value.msg == 'Invalid symbol.'
