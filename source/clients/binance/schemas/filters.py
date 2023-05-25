from decimal import Decimal

from pydantic import BaseModel


class NotionalFilter(BaseModel):
    filterType: str
    minNotional: Decimal
    applyMinToMarket: bool
    maxNotional: Decimal
    applyMaxToMarket: bool
    avgPriceMins: int


class LotSizeFilter(BaseModel):
    filterType: str
    minQty: Decimal
    maxQty: Decimal
    stepSize: Decimal
