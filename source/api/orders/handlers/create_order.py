import random
from decimal import Decimal
from typing import cast

from source.api.orders.schemas import CreateOrderRequest, CreateOrderResponse
from source.clients.binance.client import BinanceClient
from source.clients.binance.schemas.filters import LotSizeFilter, NotionalFilter, PriceFilter
from source.clients.binance.schemas.market.errors import NotFoundSymbolInExchangeInfo
from source.clients.binance.schemas.market.schemas import ExchangeInfoResponse, Symbol
from source.clients.binance.schemas.order.schemas import NewOrderRequest
from source.clients.binance.schemas.wallet.schemas import APITradingStatusResponse
from source.enums import OrderType, SymbolStatus, TimeInForce
from source.logger import logger


def _get_notional_filter(symbol: Symbol) -> NotionalFilter:
    return cast(NotionalFilter, symbol.get_filter('NOTIONAL', NotionalFilter))


def _get_lot_size_filter(symbol: Symbol) -> LotSizeFilter:
    return cast(LotSizeFilter, symbol.get_filter('LOT_SIZE', LotSizeFilter))


def _get_price_filter(symbol: Symbol) -> PriceFilter:
    return cast(PriceFilter, symbol.get_filter('PRICE_FILTER', PriceFilter))


async def create_order_handler(request: CreateOrderRequest) -> CreateOrderResponse:
    async with BinanceClient() as client:
        status: APITradingStatusResponse = await client.get_api_trading_status()
        if status.data.isLocked:
            return CreateOrderResponse(
                success=False,
                error='API trading function is locked',
            )
        exchange_info: ExchangeInfoResponse = await client.exchange_info(request.symbol)
        try:
            symbol = exchange_info.get_symbol(request.symbol.upper())
        except NotFoundSymbolInExchangeInfo:
            logger.warning(f'Not found symbol in exchange info symbol={request.symbol}')
            return CreateOrderResponse(
                success=False,
                error='Not found trading symbol',
            )
        if not symbol.isSpotTradingAllowed:
            logger.warning(f'Spot trading disabled symobl={request.symbol}')
            return CreateOrderResponse(
                success=False,
                error='Spot trading disabled',
            )
        if symbol.status in (SymbolStatus.HALT, SymbolStatus.BREAK, SymbolStatus.AUCTION_MATCH):
            logger.warning(f'Wrong trading symbol status symbol={request.symbol}')
            return CreateOrderResponse(
                success=False,
                error='Wrong trading symbol status',
            )
        if OrderType.LIMIT not in symbol.orderTypes:
            logger.warning(f'Limit order disabled symbol={request.symbol}')
            return CreateOrderResponse(
                success=False,
                error='Limit order disabled',
            )

        # Параметры ордера, такие как price и quantity должны следовать условиям
        # которые описаны в фильтрах
        # https://binance-docs.github.io/apidocs/spot/en/#filters

        notional_filter = _get_notional_filter(symbol)
        lot_filter = _get_lot_size_filter(symbol)
        price_filter = _get_price_filter(symbol)

        step_size = lot_filter.stepSize
        tick_size = price_filter.tickSize

        quantity = notional_filter.minNotional / request.priceMin
        quantity = (quantity + step_size) - (quantity + step_size) % step_size

        orders = []
        for _ in range(request.number):
            # В ТЗ в описании схемы данных сказано, что цена выбирается случайным образом
            price = random.uniform(
                a=float(request.priceMin),
                b=float(request.priceMax),
            )
            price = Decimal(price).quantize(Decimal('0.000000'))
            price = (price + tick_size) - (price + tick_size) % tick_size

            response = await client.create_new_order(
                request=NewOrderRequest(
                    symbol=request.symbol, side=request.side, type=OrderType.LIMIT,
                    quantity=quantity, price=price, timeInForce=TimeInForce.GTC,
                ),
            )
    return CreateOrderResponse(success=True)
