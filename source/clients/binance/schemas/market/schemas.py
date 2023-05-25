from typing import Dict, List, Type

from pydantic import BaseModel

from source.clients.binance.schemas.market.errors import NotFoundSymbolInExchangeInfo
from source.enums import OrderType, SymbolStatus


class Symbol(BaseModel):
    symbol: str
    status: SymbolStatus
    orderTypes: List[OrderType]
    quoteOrderQtyMarketAllowed: bool
    isSpotTradingAllowed: bool
    permissions: List[str]
    filters: List[Dict]

    def get_filter(self, filter_name: str, filter_model: Type[BaseModel]) -> BaseModel:
        for _filter in self.filters:
            if _filter['filterType'] == filter_name:
                return filter_model.parse_obj(_filter)
        raise ValueError(f'Not found {filter_name} filter')


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
