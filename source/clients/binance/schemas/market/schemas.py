from decimal import Decimal
from typing import Dict, List, Type, cast

from pydantic import BaseModel, Field, validator

from source.clients.binance.schemas.filters import LotSizeFilter, NotionalFilter, PercentPriceBySideFilter, PriceFilter
from source.clients.binance.schemas.market.errors import NotFoundSymbolInExchangeInfo
from source.enums import OrderType, SymbolStatus


class Symbol(BaseModel):
    symbol: str
    status: SymbolStatus
    orderTypes: List[OrderType]
    quoteOrderQtyMarketAllowed: bool
    isSpotTradingAllowed: bool
    permissions: List[str]
    filters: List[Dict] = Field(description='https://binance-docs.github.io/apidocs/spot/en/#filters')

    def _get_filter(self, filter_name: str, filter_model: Type[BaseModel]) -> BaseModel:
        for _filter in self.filters:
            if _filter['filterType'] == filter_name:
                return filter_model.parse_obj(_filter)
        raise ValueError(f'Not found {filter_name} filter')

    @property
    def notional_filter(self) -> NotionalFilter:
        model = NotionalFilter
        return cast(model, self._get_filter('NOTIONAL', model))

    @property
    def lot_size_filter(self) -> LotSizeFilter:
        model = LotSizeFilter
        return cast(model, self._get_filter('LOT_SIZE', model))

    @property
    def price_filter(self) -> PriceFilter:
        model = PriceFilter
        return cast(model, self._get_filter('PRICE_FILTER', model))

    @property
    def percent_price_by_side_filter(self) -> PercentPriceBySideFilter:
        model = PercentPriceBySideFilter
        return cast(model, self._get_filter('PERCENT_PRICE_BY_SIDE', model))


class ExchangeInfoResponse(BaseModel):
    """
    Поля оставил только те, которые непосредственно использую
    Понятно, что в респонсе их гораздо больше.
    """
    symbols: List[Symbol]

    def get_symbol(self, symbol: str) -> Symbol:
        for symbol_data in self.symbols:
            if symbol_data.symbol == symbol:
                return symbol_data
        raise NotFoundSymbolInExchangeInfo('Not found symbol')


class LatestPriceResponse(BaseModel):
    symbol: str
    price: Decimal

    @validator('price')
    def _dec_value(cls, value: Decimal) -> Decimal:
        return value.quantize(Decimal('0.000000'))
