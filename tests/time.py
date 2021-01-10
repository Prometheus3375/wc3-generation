import timeit
from enum import Enum, unique
from math import sqrt
from time import perf_counter_ns
from typing import Any


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


def repeat(stmt: str, setup: str = 'pass', repeat_: int = 100, number: int = 1_00_000,
           globals_: dict[str, Any] = None, measure: Measure = None) -> str:
    values = timeit.repeat(
        stmt=stmt,
        setup=setup,
        timer=perf_counter_ns,
        repeat=repeat_,
        number=number,
        globals=globals_
    )
    values = [v / number for v in values]
    mean = sum(values) / len(values)
    std = 3 * sqrt(sum((v - mean) * (v - mean) for v in values) / len(values))
    if not measure:
        measure = Measure.get(min(mean, std))
    mean = Measure.convert(mean, measure)
    std = Measure.convert(std, measure)

    return (
        f'{mean: >6.1f} ± {std: >6.1f} {measure} per loop '
        f'({repeat_:,} runs, {number:,} loops each)'
    )
