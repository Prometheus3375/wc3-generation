from collections.abc import Iterable
from sys import getsizeof

from ._helper import AbstractBijectiveMap, T1_co, T2_co, Tup_co


class FrozenBijectiveMap(AbstractBijectiveMap[T1_co, T2_co]):
    __slots__ = '_hash',

    def __init__(self, iterable: Iterable[Tup_co] = (), /):
        super().__init__(iterable)
        self._hash = hash(frozenset(frozenset(pair) for pair in self.pairs()))

    def __new__(cls, iterable: Iterable[Tup_co] = (), /):
        return object.__new__(cls)

    def __hash__(self, /):
        return self._hash

    def __sizeof__(self, /):
        return super().__sizeof__() + getsizeof(self._hash)
