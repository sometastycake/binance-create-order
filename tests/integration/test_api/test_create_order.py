from http import HTTPStatus

import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'volume, number, price_min, price_max, side', [
        (-1, 50, 2, 5, 'SELL'),
        (100, 0, 56.5, 65.4, 'SELL'),
        (100, 5, -1, 2.5, 'BUY'),
        (1005, 50, 12.5, 16.5, 'SIDE'),
        (50, 2, 15, 12, 'BUY'),
        (0, 1, 2, 3, 'SELL')
    ]
)
async def test_create_order_bad_request(fast_api_app, volume, number, price_min, price_max, side):
    request = {
        'symbol': 'btcusdt',
        'volume': volume,
        'number': number,
        'amountDif': 50,
        'side': side,
        'priceMin': price_min,
        'priceMax': price_max,
    }
    response = fast_api_app.post(url='/order/create', json=request)
    assert response.status_code == HTTPStatus.BAD_REQUEST
