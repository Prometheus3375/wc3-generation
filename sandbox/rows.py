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

# Traceback (most recent call last):
#   File "F:\Workspace\War3 Projects\Generation\sandbox\rows.py", line 23, in <module>
#     r.replace(dmg=10)
#   File "<string>", line 22, in replace
# ValueError: got unexpected field name 'dmg'


t = MyTuple('Hero', 10., 1)


# t._replace(u=10)

# Traceback (most recent call last):
#   File "F:\Workspace\War3 Projects\Generation\sandbox\rows.py", line 33, in <module>
#     t._replace(u=10)
#   File "f:\software\python3.9\lib\collections\__init__.py", line 450, in _replace
#     raise ValueError(f'Got unexpected field names: {list(kwds)!r}')
# ValueError: Got unexpected field names: ['u']


class IT:
    def __iter__(self):
        raise NotImplementedError(f'not implemented')


MyRow.fields = IT()
# repr(r)

# Traceback (most recent call last):
#   File "F:\Workspace\War3 Projects\Generation\sandbox\rows.py", line 41, in <module>
#     repr(r)
#   File "<string>", line 31, in __repr__
#   File "F:\Workspace\War3 Projects\Generation\sandbox\rows.py", line 37, in __iter__
#     raise NotImplementedError(f'not implemented')
# NotImplementedError: not implemented


# class NewRow(MyRow):
#     pass

# Traceback (most recent call last):
#   File "F:\Workspace\War3 Projects\Generation\sandbox\rows.py", line 60, in <module>
#     class NewRow(MyRow):
#   File "<string>", line 40, in __init_subclass__
# TypeError: type MyRow is not an acceptable base type
