from types import GenericAlias
from typing import NamedTuple

from misclib import except_


class LIST:
    pass


class MyList(list[list], LIST):
    lol: int

    def method(self):
        orig_bases: tuple[GenericAlias, ...] = self.__orig_bases__
        print(
            f'{self.__class__.__name__} test\n'
            f'  bases: {self.__class__.__bases__}\n'
            f'  orig bases: {orig_bases}\n'
            f'  1st orig base params: {orig_bases[0].__parameters__}\n'
            f'  1st orig base origin: {orig_bases[0].__origin__}\n'
            f'  1st orig base args: {orig_bases[0].__args__}\n'
        )


class MySubList(MyList):
    lol = 1


class MyList2(list):
    pass


class MyTuple(NamedTuple):
    id: int
    info: str


l = MyList()
l.method()
# print(MyList2[list])  # MyList2 must be generic


print(
    'NamedTuple special attributes\n'
    f'  _fields: {MyTuple._fields}\n'
    f'  __annotations__: {MyTuple.__annotations__}\n'
    f'  _field_defaults: {MyTuple._field_defaults}\n'
)

t = MyTuple(1, 'info')
print(type(t._asdict()))

except_(lambda: print(MyList.lol))
except_(MyTuple, 1, 'info', 1.0)
except_(MyTuple, 1)
