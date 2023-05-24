from typing import Dict, List

from pydantic import BaseModel

from source.api.orders.errors import NotFoundSymbolInExchangeInfo
from source.enums import OrderType, SymbolStatus


class Symbol(BaseModel):
    symbol: str
    status: SymbolStatus
    baseAsset: str
    baseAssetPrecision: int
    quote_asset: str
    quotePrecision: int
    quoteAssetPrecision: int
    baseCommissionPrecision: int
    quoteCommissionPrecision: int
    order_types: List[OrderType]
    quoteOrderQtyMarketAllowed: bool
    isSpotTradingAllowed: bool
    permissions: List[str]
    filters: List[Dict]

    class Config:
        fields = {
            'order_types': 'orderTypes',
            'quote_asset': 'quoteAsset',
        }


class ExchangeInfoResponse(BaseModel):
    timezone: str
    serverTime: int
    symbols: List[Symbol]

    def get_symbol(self, symbol: str) -> Symbol:
        for symbol_data in self.symbols:
            if symbol_data.symbol == symbol:
                return symbol_data
        raise NotFoundSymbolInExchangeInfo('Not found symbol')
