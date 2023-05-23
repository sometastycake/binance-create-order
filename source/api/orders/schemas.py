from decimal import Decimal

import pydantic
from pydantic import Field

from source.api.orders.enums import OrderSide


class CreateOrderRequest(pydantic.BaseModel):
    symbol: str = Field(description='Торговая пара')
    volume: Decimal = Field(description='Объем в долларах', gt=0)
    number: int = Field(description='На сколько ордеров нужно разбить этот объем', gt=0)
    amountDif: Decimal = Field(
        description=(
            'Разброс в долларах, в пределах которого случайным образом '
            'выбирается объем в верхнюю и нижнюю сторону'
        ),
        gt=0,
    )
    side: OrderSide = Field(description='Сторона торговли (SELL или BUY)')
    priceMin: Decimal = Field(
        description=(
            'Нижний диапазон цены, в пределах которого нужно случайным образом выбрать цену'
        ),
        ge=0,
    )
    priceMax: Decimal = Field(
        description=(
            'Верхний диапазон цены, в пределах которого нужно случайным образом выбрать цену'
        ),
        ge=0,
    )
