from decimal import Decimal

from pydantic import BaseModel, validator


class PriceFilter(BaseModel):
    filterType: str
    minPrice: Decimal
    maxPrice: Decimal
    tickSize: Decimal

    @validator('minPrice', 'maxPrice', 'tickSize')
    def _dec_value(cls, value: Decimal) -> Decimal:
        return value.quantize(Decimal('0.000000'))


class NotionalFilter(BaseModel):
    filterType: str
    minNotional: Decimal
    applyMinToMarket: bool
    maxNotional: Decimal
    applyMaxToMarket: bool
    avgPriceMins: int

    @validator('minNotional', 'maxNotional')
    def _dec_value(cls, value: Decimal) -> Decimal:
        return value.quantize(Decimal('0.000000'))


class LotSizeFilter(BaseModel):
    filterType: str
    minQty: Decimal
    maxQty: Decimal
    stepSize: Decimal

    @validator('minQty', 'maxQty', 'stepSize')
    def _dec_value(cls, value: Decimal) -> Decimal:
        return value.quantize(Decimal('0.000000'))


class PercentPriceBySideFilter(BaseModel):
    filterType: str
    bidMultiplierUp: Decimal
    bidMultiplierDown: Decimal
    askMultiplierUp: Decimal
    askMultiplierDown: Decimal
    avgPriceMins: int

    @validator('bidMultiplierUp', 'bidMultiplierDown', 'askMultiplierUp', 'askMultiplierDown')
    def _dec_value(cls, value: Decimal) -> Decimal:
        return value.quantize(Decimal('0.000000'))
