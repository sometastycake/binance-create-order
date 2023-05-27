import random
from decimal import Decimal
from typing import List, Tuple

from source.api.orders.handlers.errors import TooLowRequestedVolumeError, WrongPriceRangeError
from source.api.orders.schemas import CreateOrderData, CreateOrderRequest, CreateOrderResponse
from source.clients.binance.client import BinanceClient
from source.clients.binance.schemas.market.errors import NotFoundSymbolInExchangeInfo
from source.clients.binance.schemas.market.schemas import ExchangeInfoResponse, Symbol
from source.clients.binance.schemas.order.schemas import NewOrderRequest
from source.clients.binance.schemas.wallet.schemas import APITradingStatusResponse
from source.enums import OrderSide, OrderType, SymbolStatus, TimeInForce
from source.logger import logger


def _calculate_price(price_min: Decimal, price_max: Decimal, tick_size: Decimal) -> Decimal:
    """
    Вычисление цен ордеров
    Исхожу из того, что в ТЗ в описании схемы сказано, что цены из диапазона
    берутся случайным образом.
    Дополнительно, значение цены должно удовлетворять условиям из PRICE_FILTER, т.е.
    price % tick_size = 0
    """
    price = random.uniform(
        a=float(price_min),
        b=float(price_max),
    )
    price_dec = Decimal(price).quantize(Decimal('0.000000'))
    return (price_dec + tick_size) - (price_dec + tick_size) % tick_size


def _calculate_lots(
        prices: List[Decimal], min_quantity: Decimal, step_size: Decimal, volume: Decimal,
) -> List[Decimal]:
    """
    На данном этапе имеем список цен prices и теперь нужно для каждой цены
    рассчитать значение quantity, т.е. необходимо выполнение условия
    Σ(Pi * Qi) = volume, где Pi - цена, Qi - quantity
    """
    lots = []
    for _ in range(len(prices)):
        lots.append(min_quantity)  # Изначально каждому Pi присваиваем минимальное quantity
    current_volume = Decimal(0)
    for price, quantity in zip(prices, lots):
        current_volume += price * quantity  # Считаем получившийся объем
    if volume < current_volume:
        raise TooLowRequestedVolumeError
    # TODO пока не успеваю доделать
    return lots


async def _process_price_range(
        request: CreateOrderRequest, client: BinanceClient, symbol: Symbol,
) -> Tuple[Decimal, Decimal]:
    """
    Для лимитных ордеров есть допустимый диапазон цен, по
    которым мы можем закинуть ордер в стакан.
    Есть случаи, при которых мы не можем залить ордера в стакан
    Например
    Диапазон цен, пришедший с api: [2; 5] или [9; 11]
    Допустимый диапазон цен в стакане: [6; 8]
    В данном случае по нашему диапазону не сможем создать ордера и должны выдать ошибку
    """
    Filter = symbol.percent_price_by_side_filter

    price = (await client.get_latest_price(request.symbol)).price

    # См. фильтр PERCENT_PRICE_BY_SIDE
    # https://binance-docs.github.io/apidocs/spot/en/#filters
    if request.side is OrderSide.BUY:
        price_up = price * Filter.bidMultiplierUp
        price_down = price * Filter.bidMultiplierDown
    else:
        price_up = price * Filter.askMultiplierUp
        price_down = price * Filter.askMultiplierDown

    # Если диапазон с api полностью лежит за пределами допустимого диапазона без пересечений
    if request.priceMax <= price_down or request.priceMin >= price_up:
        raise WrongPriceRangeError

    # Если допустимый диапазон цен пересекается с диапазоном, полученным в api
    # то корректируем границы цен
    # TODO нужно больше контекста задачи, это лишь мое мнение, что нужно так сделать
    price_min = price_down if request.priceMin < price_down else request.priceMin
    price_max = price_up if request.priceMax > price_up else request.priceMax

    return price_min, price_max


async def create_order_handler(request: CreateOrderRequest, client: BinanceClient) -> CreateOrderResponse:
    """
    Разбиение request.volume объема на request.number ордеров

    Важно:
        Не полностью понял ТЗ, особенно момент с amountDif, потому
        сделал просто разбиение обшего объема на request.number ордеров =(
    """
    status: APITradingStatusResponse = await client.get_api_trading_status()
    if status.data.isLocked:
        logger.error('API trading function is locked')
        return CreateOrderResponse(
            success=False,
            error='API trading function is locked',
        )
    exchange_info: ExchangeInfoResponse = await client.exchange_info(request.symbol)
    try:
        symbol = exchange_info.get_symbol(request.symbol.upper())
    except NotFoundSymbolInExchangeInfo:
        logger.error('Not found symbol in exchange info')
        return CreateOrderResponse(
            success=False,
            error='Not found trading symbol',
        )
    if not symbol.isSpotTradingAllowed:
        logger.error('Spot trading disabled')
        return CreateOrderResponse(
            success=False,
            error='Spot trading disabled',
        )
    if symbol.status in (SymbolStatus.HALT, SymbolStatus.BREAK, SymbolStatus.AUCTION_MATCH):
        logger.error('Wrong trading symbol status')
        return CreateOrderResponse(
            success=False,
            error='Wrong trading symbol status',
        )

    # TODO по хорошему нужно проверки выше выносить в middleware
    # так как они выглядят как общие для некоторого ряда api

    # Исхожу из того, что в схеме есть диапазон цен, по которому нужно раскинуть ордера
    # значит MARKET ордер нам не подходит и нужно использовать лимитку
    if OrderType.LIMIT not in symbol.orderTypes:
        logger.error('Limit order disabled')
        return CreateOrderResponse(
            success=False,
            error='Limit order disabled',
        )

    try:
        price_min, price_max = await _process_price_range(request, client, symbol)
    except WrongPriceRangeError:
        logger.error('Wrong price range')
        return CreateOrderResponse(
            success=False,
            error='Wrong price range',
        )

    step_size = symbol.lot_size_filter.stepSize
    tick_size = symbol.price_filter.tickSize

    # Минимально возможное значение quantity
    min_quantity = symbol.notional_filter.minNotional / request.priceMin
    min_quantity = (min_quantity + step_size) - (min_quantity + step_size) % step_size

    prices = []
    for _ in range(request.number):
        prices.append(_calculate_price(price_min, price_max, tick_size))

    try:
        lots = _calculate_lots(prices, min_quantity, step_size, request.volume)
    except TooLowRequestedVolumeError:
        logger.error('Too low requested volume')
        return CreateOrderResponse(
            success=False,
            error='Too low requested volume',
        )

    orders = []
    for price, quantity in zip(prices, lots):
        # TODO тут остаются неопределенные моменты
        # Например, если ордеров много и есть вариант попасть на rate limits
        # по этой же причине нельзя закинуть реквесты в asyncio.gather
        # и вызывающий api код может попасть на 504 gateway timeout
        response = await client.create_new_order(
            request=NewOrderRequest(
                symbol=request.symbol, side=request.side, type=OrderType.LIMIT,
                quantity=quantity, price=price, timeInForce=TimeInForce.GTC,
            ),
        )
        orders.append(CreateOrderData(
            order_id=response.orderId,
            price=response.price,
            transact_time=response.transactTime,
        ))
    return CreateOrderResponse(success=True, orders=orders)
