from decimal import Decimal
from typing import List, Tuple, Union

from pydantic import BaseModel


def convert_values_list_to_decimal(values: List[Union[int, float]]) -> List[Decimal]:
    return list(map(lambda value: Decimal(value).quantize(Decimal('0.000000')), values))


class _ParamModel(BaseModel):
    prices: List[Decimal]
    min_quantity: Decimal
    step: Decimal
    volume: Decimal
    expected_lots: List[Decimal]

    def to_tuple(self) -> Tuple[List[Decimal], Decimal, Decimal, Decimal, List[Decimal]]:
        return self.prices, self.min_quantity, self.step, self.volume, self.expected_lots


_parametrize = [
    _ParamModel(
        prices=convert_values_list_to_decimal([1, 1.1, 0.8, 1.4]),
        min_quantity=Decimal(16),
        step=Decimal(1),
        volume=Decimal(100),
        expected_lots=convert_values_list_to_decimal([32, 29, 17, 16]),
    ),
    _ParamModel(
        prices=convert_values_list_to_decimal([10, 12, 11]),
        min_quantity=Decimal(1),
        step=Decimal(1),
        volume=Decimal(104),
        expected_lots=convert_values_list_to_decimal([3, 3, 3]),
    ),
    _ParamModel(
        prices=convert_values_list_to_decimal([0.068, 0.070, 0.072, 0.074]),
        min_quantity=Decimal(64),
        step=Decimal(0.04),
        volume=Decimal(56),
        expected_lots=convert_values_list_to_decimal([213.64, 192, 192, 192]),
    ),
    _ParamModel(
        prices=convert_values_list_to_decimal([23, 23.5, 22]),
        min_quantity=Decimal(2),
        step=Decimal(1.5),
        volume=Decimal(1076.6),
        expected_lots=convert_values_list_to_decimal([16, 16, 14]),
    ),
    _ParamModel(
        prices=convert_values_list_to_decimal([200, 220, 250, 275, 216]),
        min_quantity=Decimal(1),
        step=Decimal(1),
        volume=Decimal(10000),
        expected_lots=convert_values_list_to_decimal([9, 9, 9, 8, 8]),
    ),
    _ParamModel(
        prices=convert_values_list_to_decimal([0.5]),
        min_quantity=Decimal(14),
        step=Decimal(1),
        volume=Decimal(7),
        expected_lots=convert_values_list_to_decimal([14]),
    ),
]


def get_parametrize_for_calculate_lots_test() -> List[Tuple[List[Decimal], Decimal, Decimal, Decimal, List[Decimal]]]:
    return [param.to_tuple() for param in _parametrize]
