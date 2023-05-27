from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, validator

from source.clients.binance.signature import BaseSignature
from source.enums import OrderSide, OrderType, TimeInForce


class NewOrderRequest(BaseSignature):
    symbol: str
    side: OrderSide
    type: OrderType
    quantity: Optional[Decimal] = None
    price: Optional[Decimal] = None
    timeInForce: Optional[TimeInForce] = None

    class Config:
        use_enum_values = True

    @validator('symbol', pre=True)
    def _symbol(cls, symbol: str) -> str:
        return symbol.upper()

    @validator('quantity', 'price', pre=True)
    def _dec_value(cls, value: Optional[Decimal]) -> Optional[Decimal]:
        if value is None:
            return value
        return value.quantize(Decimal('0.000000'))


class NewOrderResponse(BaseModel):
    symbol: str
    orderId: int
    transactTime: int
    price: Decimal
    status: str
    timeInForce: TimeInForce
    type: OrderType
    side: OrderSide

    @validator('price')
    def _dec_value(cls, value: Optional[Decimal]) -> Optional[Decimal]:
        if value is None:
            return value
        return value.quantize(Decimal('0.000000'))
