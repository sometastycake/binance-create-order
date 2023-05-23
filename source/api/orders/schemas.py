from decimal import Decimal

import pydantic
from pydantic import Field

from source.api.orders.enums import OrderSide


class CreateOrderRequest(pydantic.BaseModel):
    symbol: str = Field(description='Торговая пара')
    volume: Decimal = Field(description='Объем в долларах')
    number: int = Field(description='На сколько ордеров нужно разбить этот объем')
    amountDif: Decimal = Field(description=(
        'Разброс в долларах, в пределах которого случайным образом '
        'выбирается объем в верхнюю и нижнюю сторону'
    ))
    side: OrderSide = Field(description='Сторона торговли (SELL или BUY)')
    priceMin: Decimal = Field(description=(
        'Нижний диапазон цены, в пределах которого нужно случайным образом выбрать цену'
    ))
    priceMax: Decimal = Field(description=(
        'Верхний диапазон цены, в пределах которого нужно случайным образом выбрать цену'
    ))
