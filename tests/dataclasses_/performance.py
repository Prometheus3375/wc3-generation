import sys
from collections.abc import Callable
from typing import Any

from tests.time import repeat
from .classes import (
    DataClass,
    FrozenDataClass,
    ImmutableObject,
    ImmutableObjectObject, ImmutableObjectSuper,
    NamedTupleSub,
    Object,
    ObjectNoSlots,
)


# TODO Make special structure where class creation, attribute access is described to allow easy tests


class Test:
    def __init__(self, args: str, *classes: type):
        self._classes = tuple(classes)
        self.args = args
        self.globals = {cls.__name__: cls for cls in self._classes}
        l = max(len(cls.__name__) for cls in self._classes)
        self._namef = f' <{l}'

    def _testprint(self, cls: type, func: Callable[[type], Any]):
        print(f'  {cls.__name__:{self._namef}}: {func(cls)}')

    def _test(self, name: str, func: Callable[[type], Any]):
        print(f'Test {name}')
        for cls in self._classes:
            self._testprint(cls, func)
        print()

    def memory(self, args: tuple):
        self._test('memory usage', lambda cls: f'{sys.getsizeof(cls(*args))} b')

    def create(self):
        self._test('creation speed',
                   lambda cls: repeat(
                       f'{cls.__name__}({self.args})',
                       globals_=self.globals
                   ))

    def attribute_access(self, attribute: str):
        self._test(f'attribute {attribute} access',
                   lambda cls: repeat(
                       stmt=f'data.{attribute}',
                       setup=f'data = {cls.__name__}({self.args})',
                       globals_=self.globals
                   ))

    def method_call(self, method: str, args: str = ''):
        self._test(f'{method}({args}) call',
                   lambda cls: repeat(
                       stmt=f'data.{method}({args})',
                       setup=f'data = {cls.__name__}({self.args})',
                       globals_=self.globals
                   ))


def main():
    args = 1,
    strargs = '1'
    test = Test(
        strargs, DataClass, FrozenDataClass, Object, ObjectNoSlots, ImmutableObject, ImmutableObjectSuper,
        ImmutableObjectObject,
        NamedTupleSub
    )
    test.memory(args)
    test._testprint(dict, lambda cls: f'{sys.getsizeof(cls(field1=1, field2=0))} b')
    test.create()
    test._testprint(dict, lambda cls: repeat(
        f'{cls.__name__}(field1=1, field2=0)',
        globals_=dict(dict=dict)
    ))
    test.attribute_access('field1')
    test._testprint(dict, lambda cls: repeat(
        stmt=f'data["field1"]',
        setup=f'data = {cls.__name__}(field1=1, field2=0)',
        globals_=dict(dict=dict)
    ))
    test.method_call('method')
    test.method_call('method2')


if __name__ == '__main__':
    main()
