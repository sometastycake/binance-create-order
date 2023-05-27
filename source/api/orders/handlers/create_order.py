import random
from decimal import Decimal

from source.api.orders.handlers.errors import WrongPriceRangeError
from source.api.orders.schemas import CreateOrderRequest, CreateOrderResponse
from source.clients.binance.client import BinanceClient
from source.clients.binance.schemas.market.errors import NotFoundSymbolInExchangeInfo
from source.clients.binance.schemas.market.schemas import ExchangeInfoResponse, Symbol
from source.clients.binance.schemas.order.schemas import NewOrderRequest
from source.clients.binance.schemas.wallet.schemas import APITradingStatusResponse
from source.enums import OrderSide, OrderType, SymbolStatus, TimeInForce
from source.logger import logger


def _generate_price(price_min: Decimal, price_max: Decimal, tick_size: Decimal) -> Decimal:
    """
    В ТЗ в описании схемы сказано, что цена выбирается случайным образом.
    """
    price = random.uniform(
        a=float(price_min),
        b=float(price_max),
    )
    price = Decimal(price).quantize(Decimal('0.000000'))
    return (price + tick_size) - (price + tick_size) % tick_size


async def _process_price_range(request: CreateOrderRequest, client: BinanceClient, symbol: Symbol):
    """
    Для лимитных ордеров есть допустимый диапазон цен, по
    которым мы можем закинуть ордер в стакан.
    """
    _filter = symbol.percent_price_by_side_filter

    price = await client.get_latest_price(request.symbol)

    if request.side is OrderSide.BUY:
        price_up = price.price * _filter.bidMultiplierUp
        price_down = price.price * _filter.bidMultiplierDown
    else:
        price_up = price.price * _filter.askMultiplierUp
        price_down = price.price * _filter.askMultiplierDown

    # Если диапазон с api полностью лежит за пределами допустимого диапазона без пересечений
    if request.priceMax <= price_down or request.priceMin >= price_up:
        raise WrongPriceRangeError

    # Если допустимый диапазон цен пересекается с диапазоном, полученным в api
    # то корректируем границы цен
    price_min = price_down if request.priceMin < price_down else request.priceMin
    price_max = price_up if request.priceMax > price_up else request.priceMax

    return price_min, price_max


async def create_order_handler(request: CreateOrderRequest, client: BinanceClient) -> CreateOrderResponse:
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

    try:
        price_min, price_max = await _process_price_range(request, client, symbol)
    except WrongPriceRangeError:
        return CreateOrderResponse(
            success=False,
            error='Wrong price range',
        )

    step_size = symbol.lot_size_filter.stepSize
    tick_size = symbol.price_filter.tickSize

    # Минимально возможное значение quantity
    quantity = symbol.notional_filter.minNotional / request.priceMin
    quantity = (quantity + step_size) - (quantity + step_size) % step_size

    if request.volume < price_min * quantity:
        return CreateOrderResponse(
            success=False,
            error='Too low requested volume'
        )

    prices = []
    for _ in range(request.number):
        prices.append(_generate_price(price_min, price_max, tick_size))

    # На данном этапе имеем список цен prices и теперь нужно
    # для каждой цены рассчитать значение quantity, т.е.
    # sum(Pi * Qi) = volume, где Pi - цена, Qi - quantity

    orders = []
    volume = request.volume
    for price in prices:
        response = await client.create_new_order(
            request=NewOrderRequest(
                symbol=request.symbol, side=request.side, type=OrderType.LIMIT,
                quantity=quantity, price=price, timeInForce=TimeInForce.GTC,
            ),
        )
    return CreateOrderResponse(success=True)
