from decimal import Decimal
from typing import Dict, List, Optional

import pydantic
from pydantic import Field, root_validator

from source.enums import OrderSide


class CreateOrderRequest(pydantic.BaseModel):
    symbol: str = Field(description='Торговая пара')
    volume: Decimal = Field(description='Объем в долларах', gt=0)
    number: int = Field(description='На сколько ордеров нужно разбить этот объем', gt=0)
    amountDif: Decimal = Field(
        gt=0,
        description=(
            'Разброс в долларах, в пределах которого случайным образом '
            'выбирается объем в верхнюю и нижнюю сторону'
        ),
    )
    side: OrderSide = Field(description='Сторона торговли (SELL или BUY)')
    priceMin: Decimal = Field(
        gt=0,
        description=(
            'Нижний диапазон цены, в пределах которого нужно случайным образом выбрать цену'
        ),
    )
    priceMax: Decimal = Field(
        gt=0,
        description=(
            'Верхний диапазон цены, в пределах которого нужно случайным образом выбрать цену'
        ),
    )

    @root_validator
    def _root(cls, values: Dict) -> Dict:
        if 'priceMin' not in values or 'priceMax' not in values:
            return values
        price_min = values['priceMin']
        price_max = values['priceMax']
        if price_min > price_max:
            raise ValueError('priceMax cannot be less than priceMin')
        return values


class CreateOrderData(pydantic.BaseModel):
    order_id: int
    price: Decimal
    transact_time: int


class CreateOrderResponse(pydantic.BaseModel):
    success: bool
    error: Optional[str]
    orders: Optional[List[CreateOrderData]]
