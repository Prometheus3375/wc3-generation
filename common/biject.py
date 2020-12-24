from collections import Iterable
from typing import Collection, Generic, Iterator, TypeVar, Union

_T1 = TypeVar('_T1')
_T2 = TypeVar('_T2')
_K = Union[_T1, _T2]
_V = tuple[_T1, _T2]


class BijectiveMap(Generic[_T1, _T2], Collection):
    __slots__ = '_data'

    def __init__(self, iterable: Iterable[_V] = ()):
        self._data: dict[_K, _V] = {}
        for t1, t2 in iterable:
            self.update(t1, t2)

    def _add(self, v1: _T1, v2: _T2):
        t = v1, v2
        self._data[v1] = t
        self._data[v2] = t

    def add(self, v1: _T1, v2: _T2):
        if v1 in self._data:
            v = v1
        elif v2 in self._data:
            v = v2
        else:
            self._add(v1, v2)
            return

        raise ValueError(f'Value {v} is already bound to {self[v]}')

    def update(self, v1: _T1, v2: _T2):
        if v1 in self._data:
            self.__delitem__(v1)
        if v2 in self._data:
            self.__delitem__(v2)
        self._add(v1, v2)

    def __delitem__(self, value: _K):
        t1, t2 = self._data[value]
        if value is t1 or value == t1 or value is t2 or value == t2:
            del self._data[t1]
            del self._data[t2]
        else:
            raise KeyError(f'Key {value} points to tuple ({t1}, {t2}) which does contain it')

    def __getitem__(self, value: _K) -> _K:
        t1, t2 = self._data[value]
        if value is t1 or value == t1:
            return t2

        if value is t2 or value == t2:
            return t1

        raise KeyError(f'Key {value} points to tuple ({t1}, {t2}) which does contain it')

    def __len__(self) -> int:
        return len(self._data) // 2

    def __contains__(self, value: _K):
        return value in self._data

    def values(self) -> set[_K]:
        return set(self._data.keys())

    def items(self) -> set[_V]:
        return set(self._data.values())

    def __iter__(self) -> Iterator[_K]:
        return iter(self._data.keys())

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._data == other._data

        raise TypeError(f'An attempt to compare types {type(self)} and {type(other)}')

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return self._data != other._data

        raise TypeError(f'An attempt to compare types {type(self)} and {type(other)}')

    def clear(self):
        self._data.clear()

    def __repr__(self):
        entries = ', '.join(str(v) for v in self.items())
        return f'{self.__class__.__name__}[{entries}]'
