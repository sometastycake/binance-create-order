from decimal import Decimal
from typing import Optional

from pydantic import validator

from source.clients.binance.signature import BaseSignature
from source.enums import OrderSide, OrderType, TimeInForce


class CheckOrderStatusRequest(BaseSignature):
    symbol: str
    orderId: Optional[int] = None
    origClientOrderId: Optional[str] = None

    @validator('symbol', pre=True)
    def _symbol(cls, symbol: str) -> str:
        return symbol.upper()


class NewOrderRequest(BaseSignature):
    symbol: str
    side: OrderSide
    type: OrderType
    quantity: Optional[Decimal] = None
    quoteOrderQty: Optional[Decimal] = None
    price: Optional[Decimal] = None
    newClientOrderId: Optional[str] = None
    timeInForce: Optional[TimeInForce] = None

    class Config:
        use_enum_values = True

    @validator('symbol', pre=True)
    def _symbol(cls, symbol: str) -> str:
        return symbol.upper()
