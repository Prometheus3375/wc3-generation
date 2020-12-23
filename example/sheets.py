from typing import NamedTuple

from lib.sheet import Sheet, SingletonSheet


class MyRow(NamedTuple):
    name: str
    damage: float
    level: int


class MySheet(Sheet[MyRow]):
    column_names = 'name', 'damage', 'level'
    column_conversions = str, float, int


class MyOnlySheet(SingletonSheet[MyRow]):
    column_names = 'name', 'damage', 'level'
