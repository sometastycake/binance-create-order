from source.api.orders.schemas import CreateOrderRequest, CreateOrderResponse
from source.clients.binance.client import BinanceClient
from source.clients.binance.schemas.market.errors import NotFoundSymbolInExchangeInfo
from source.clients.binance.schemas.market.schemas import ExchangeInfoResponse
from source.enums import OrderType, SymbolStatus
from source.logger import logger


async def create_order_handler(request: CreateOrderRequest) -> CreateOrderResponse:
    async with BinanceClient(raise_if_error=True) as client:
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
    return CreateOrderResponse(success=True)
