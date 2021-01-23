from collections.abc import Mapping, MappingView, Set
from sys import getsizeof
from typing import Generic, Iterable, Iterator, Optional, TypeVar, Union, overload

T1 = TypeVar('T1')
T2 = TypeVar('T2')
KV = Union[T1, T2]
Tup = tuple[T1, T2]

T1_co = TypeVar('T1_co', covariant=True)
T2_co = TypeVar('T2_co', covariant=True)
KV_co = Union[T1_co, T2_co]
Tup_co = tuple[T1_co, T2_co]

T = TypeVar('T')


def unique_pairs(iterable: Iterable[Tup], mapping: dict = None, /) -> dict[KV, KV]:
    d = {} if mapping is None else mapping
    default = object()
    for value1, value2 in iterable:
        d.pop(d.pop(value1, default), default)
        d.pop(d.pop(value2, default), default)
        d[value1] = value2
        d[value2] = value1

    return d


@MappingView.register
class PairsView(Generic[T1, T2], Set[Tup]):
    __slots__ = '_source',

    def __init__(self, source: 'AbstractBijectiveMap[T1, T2]', /):
        self._source = source

    def __len__(self, /):
        return len(self._source) // 2

    def __contains__(self, pair: Tup, /):
        return pair[0] == self._source.get(pair[1], object())

    def __iter__(self, /) -> Iterator[Tup]:
        seen = set()
        for v1, v2 in self._source.items():
            if (v2, v1) in seen:
                continue

            pair = v1, v2
            seen.add(pair)
            yield pair

    def __reversed__(self, /) -> Iterator[Tup]:
        seen = set()
        for v2, v1 in reversed(self._source.items()):
            pair = v1, v2
            if pair in seen:
                continue

            seen.add((v2, v1))
            yield pair

    def __repr__(self, /):
        return f'{self.__class__.__name__}({self._source!r})'


@Mapping.register
class AbstractBijectiveMap(Generic[T1, T2]):
    __slots__ = '_data',

    def __init__(self, iterable: Iterable[Tup] = (), /):
        self._data: dict[KV, KV] = unique_pairs(iterable)

    def __new__(cls, /, *args, **kwargs):
        raise TypeError(f'cannot instantiate abstract class {AbstractBijectiveMap.__name__}')

    def __len__(self, /):
        return len(self._data)

    @overload
    def __getitem__(self, value: T1, /) -> T2: ...
    @overload
    def __getitem__(self, value: T2, /) -> T1: ...

    def __getitem__(self, value, /):
        return self._data[value]

    def __contains__(self, value: KV, /):
        return value in self._data

    def __iter__(self, /):
        return iter(self._data)

    def __reversed__(self, /):
        return reversed(self._data)

    @overload
    def get(self, value: T1, /) -> Optional[T2]: ...
    @overload
    def get(self, value: T2, /) -> Optional[T1]: ...
    @overload
    def get(self, value: T1, default: T2, /) -> T2: ...
    @overload
    def get(self, value: T1, default: T, /) -> Union[T2, T]: ...
    @overload
    def get(self, value: T2, default: T1, /) -> T1: ...
    @overload
    def get(self, value: T2, default: T, /) -> Union[T1, T]: ...

    def get(self, value, default=None, /):
        return self._data.get(value, default)

    def values(self, /):
        return self._data.keys()

    keys = values

    def items(self, /):
        return self._data.items()

    def pairs(self, /) -> PairsView[T1, T2]:
        return PairsView(self)

    def __str__(self, /):
        content = ', '.join(f'{v1} ~ {v2}' for v1, v2 in self.pairs())
        return f'{{{content}}}'

    def __repr__(self, /):
        return f'{self.__class__.__name__}({self})'

    def __eq__(self, other, /):
        return self._data == other

    def __ne__(self, other, /):
        return self._data != other

    def __getnewargs__(self, /) -> tuple[Tup, ...]:
        return tuple(self.pairs())

    def __sizeof__(self, /):
        return super().__sizeof__() + getsizeof(self._data)
