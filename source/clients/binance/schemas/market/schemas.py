from typing import Dict, List

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
