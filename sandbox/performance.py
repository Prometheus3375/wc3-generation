import sys
import timeit
from dataclasses import dataclass
from enum import Enum, unique
from math import sqrt
from time import perf_counter_ns
from typing import Any, Callable, NamedTuple

from common import except_


@dataclass
class DataClass:
    field1: int
    field2: int = 0

    def method(self):
        return 'Hello, I 2 fields'

    def method2(self):
        return f'Hello, I 2 fields: {self.field1} and {self.field2}'


@dataclass(frozen=True)
class FrozenDataClass:
    field1: int
    field2: int = 0

    def method(self):
        return 'Hello, I 2 fields'

    def method2(self):
        return f'Hello, I 2 fields: {self.field1} and {self.field2}'


class NamedTupleSub(NamedTuple):
    field1: int
    field2: int = 0

    def method(self):
        return 'Hello, I 2 fields'

    def method2(self):
        return f'Hello, I 2 fields: {self.field1} and {self.field2}'


class Object:
    __slots__ = 'field1', 'field2'

    def __init__(self, field1: int, field2: int = 0):
        self.field1 = field1
        self.field2 = field2

    def method(self):
        return 'Hello, I 2 fields'

    def method2(self):
        return f'Hello, I 2 fields: {self.field1} and {self.field2}'


class ImmutableObject:
    __slots__ = 'field1', 'field2'

    def __init__(self, field1: int, field2: int = 0):
        self.field1 = field1
        self.field2 = field2

    def __setattr__(self, key: str, value: Any):
        if hasattr(self, key):
            raise AttributeError(
                f'cannot assign {value} to attribute {key} '
                f'of immutable {self.__class__.__name__} instance'
            )

        super().__setattr__(key, value)

    def method(self):
        return 'Hello, I 2 fields'

    def method2(self):
        return f'Hello, I 2 fields: {self.field1} and {self.field2}'


class ImmutableObjectSuper:
    __slots__ = 'field1', 'field2'

    def __init__(self, field1: int, field2: int = 0):
        super().__setattr__('field1', field1)
        super().__setattr__('field2', field2)

    def __setattr__(self, key: str, value: Any):
        raise AttributeError(
            f'cannot assign {value} to attribute {key} '
            f'of immutable {self.__class__.__name__} instance'
        )

    def method(self):
        return 'Hello, I 2 fields'

    def method2(self):
        return f'Hello, I 2 fields: {self.field1} and {self.field2}'


@unique
class Measure(Enum):
    s = ' s'
    ms = 'ms'
    ns = 'ns'

    def __str__(self):
        return self.value

    @classmethod
    def get(cls, ns: float) -> 'Measure':
        if ns < 1_000:
            return cls.ns

        if 1_000 <= ns < 1_000_000:
            return cls.ms

        return cls.s

    @classmethod
    def convert(cls, ns: float, measure: 'Measure') -> float:
        if measure is cls.ns:
            return ns
        if measure is cls.ms:
            return ns / 1_000
        if measure is cls.s:
            return ns / 1_000_000

        raise ValueError(f'Unknown measure type {measure}')


def repeat(stmt: str, setup: str = 'pass', repeat_: int = 10, number: int = 1_000_000,
           globals_: dict[str, Any] = None, measure: str = None) -> str:
    values = timeit.repeat(
        stmt=stmt,
        setup=setup,
        timer=perf_counter_ns,
        repeat=repeat_,
        number=number,
        globals=globals_
    )
    mean = sum(values) / len(values)
    std = 3 * sqrt(sum((v - mean) * (v - mean) for v in values) / len(values))
    if not measure:
        measure = Measure.get(min(mean, std))
    mean = Measure.convert(mean, measure)
    std = Measure.convert(std, measure)

    return (
        f'{mean: >6.1f} ± {std: >6.1f} {measure} '
        f'({repeat_:,} runs, {number:,} loops each)'
    )


class Test:
    def __init__(self, args: str, *classes: type):
        self._classes = tuple(classes)
        self.args = args
        self.globals = {cls.__name__: cls for cls in self._classes}
        l = max(len(cls.__name__) for cls in self._classes)
        self._namef = f' <{l}'

    def _test(self, name: str, func: Callable[[type], Any]):
        print(f'Test {name}')
        for cls in self._classes:
            print(f'  {cls.__name__:{self._namef}}: {func(cls)}')
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
    data = ImmutableObject(1)
    except_(exec, 'data.field2 = 1', {'data': data})
    except_(exec, 'data.field3 = 1', {'data': data})
    data = FrozenDataClass(1)
    except_(exec, 'data.field2 = 1', {'data': data})

    args = 1,
    strargs = '1'
    test = Test(strargs, DataClass, FrozenDataClass, Object, ImmutableObject, ImmutableObjectSuper, NamedTupleSub)
    test.memory(args)
    test.create()
    test.attribute_access('field1')
    test.method_call('method')
    test.method_call('method2')


if __name__ == '__main__':
    main()
