from typing import NamedTuple

from common import except_


class MyList(list[list]):
    lol: int

    def method(self):
        print(
            f'{self.__class__.__name__} test\n'
            f'  bases: {self.__class__.__bases__}\n'
            f'  orig bases: {self.__orig_bases__}\n'
            f'  args of 1st orig base: {self.__orig_bases__[0].__args__}\n'
            f'  1st arg of 1st orig base: {self.__orig_bases__[0].__args__[0]}\n'
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


t = MyTuple(1, 'info')

print(MyTuple._fields)
print(MyTuple.__annotations__)
print(MyTuple._field_defaults)
print(type(t._asdict()))
t2 = t._replace(id=2)
print(t2)
except_(lambda: print(MyList.lol))
except_(MyTuple, 1, 'info', 1.0)
except_(MyTuple, 1)
