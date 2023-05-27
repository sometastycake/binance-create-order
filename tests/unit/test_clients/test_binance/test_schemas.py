from decimal import Decimal

from source.clients.binance.schemas.filters import LotSizeFilter, NotionalFilter, PercentPriceBySideFilter, PriceFilter
from source.clients.binance.schemas.market.schemas import Symbol
from source.enums import OrderType, SymbolStatus


def get_symbol() -> Symbol:
    return Symbol(
        symbol='btcusdt',
        status=SymbolStatus.TRADING,
        orderTypes=[OrderType.LIMIT],
        quoteOrderQtyMarketAllowed=True,
        isSpotTradingAllowed=True,
        permissions=['LIMIT'],
        filters=[
            {
                'filterType': 'PRICE_FILTER',
                'minPrice': '0.00001000',
                'maxPrice': '1000.00000000',
                'tickSize': '0.00001000',
            },
            {
                'filterType': 'LOT_SIZE',
                'minQty': '1.00000000',
                'maxQty': '9000000.00000000',
                'stepSize': '1.00000000',
            },
            {
                'filterType': 'PERCENT_PRICE_BY_SIDE',
                'bidMultiplierUp': '5',
                'bidMultiplierDown': '0.2',
                'askMultiplierUp': '5',
                'askMultiplierDown': '0.2',
                'avgPriceMins': 5,
            },
            {
                'filterType': 'NOTIONAL',
                'minNotional': '5.00000000',
                'applyMinToMarket': True,
                'maxNotional': '9000000.00000000',
                'applyMaxToMarket': False,
                'avgPriceMins': 5,
            },
        ],
    )


def test_symbol_notional_filter():
    symbol = get_symbol()
    notional_filter = symbol.notional_filter
    assert notional_filter == NotionalFilter(
        filterType='NOTIONAL',
        minNotional=Decimal('5.000000'),
        applyMinToMarket=True,
        maxNotional=Decimal('9000000.000000'),
        applyMaxToMarket=False,
        avgPriceMins=5,
    )


def test_symbol_price_filter():
    symbol = get_symbol()
    price_filter = symbol.price_filter
    assert price_filter == PriceFilter(
        filterType='PRICE_FILTER',
        minPrice=Decimal('0.000010'),
        maxPrice=Decimal('1000.000000'),
        tickSize=Decimal('0.000010'),
    )


def test_symbol_lot_size_filter():
    symbol = get_symbol()
    lot_size_filter = symbol.lot_size_filter
    assert lot_size_filter == LotSizeFilter(
        filterType='LOT_SIZE',
        minQty=Decimal('1.000000'),
        maxQty=Decimal('9000000.000000'),
        stepSize=Decimal('1.000000'),
    )


def test_symbol_percent_price_by_side_filter():
    symbol = get_symbol()
    percent_price_by_side_filter = symbol.percent_price_by_side_filter
    assert percent_price_by_side_filter == PercentPriceBySideFilter(
        filterType='PERCENT_PRICE_BY_SIDE',
        bidMultiplierUp=Decimal('5.000000'),
        bidMultiplierDown=Decimal('0.200000'),
        askMultiplierUp=Decimal('5.000000'),
        askMultiplierDown=Decimal('0.200000'),
        avgPriceMins=5,
    )
