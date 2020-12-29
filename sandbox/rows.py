from typing import NamedTuple

from lib.sheet import Row


def must_be_positive(*args):
    pass


class MyRow(Row):
    name: str = 'name',
    damage: float = 'damage', must_be_positive
    stat: int


class MyTuple(NamedTuple):
    name: str
    damage: float
    stat: int


r = MyRow('Hero', 10., 1)
# r.replace(dmg=10)

# print(r)
# for name in sorted(name for name in dir(MyRow) if name[:2] != '__'):
#     print(f'{name}: {getattr(MyRow, name)}')
# print(f'__module__: {MyRow.__module__}')

t = MyTuple('Hero', 10., 1)
t._replace(u=10)
