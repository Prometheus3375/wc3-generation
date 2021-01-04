from collections.abc import Iterable, Iterator, Set
from typing import ClassVar, Generic, TypeVar, Union, overload

_T1 = TypeVar('_T1')
_T2 = TypeVar('_T2')
_K = Union[_T1, _T2]
_V = tuple[_T1, _T2]


class BijectiveMapValuesView(Set[_K]):
    __slots__ = '_source'

    def __init__(self, source: 'BijectiveMap', /):
        self._source = source
        super().__init__()

    def __len__(self, /) -> int:
        return len(self._source)

    def __iter__(self, /) -> Iterator[_K]:
        for v1, v2 in self._source:
            yield v1
            yield v2

    def __contains__(self, value: _K, /) -> bool:
        return self._source.has_value(value)


class BijectiveMapItemsView(Set[_V]):
    __slots__ = '_source'

    def __init__(self, source: 'BijectiveMap', /):
        self._source = source
        super().__init__()

    def __len__(self, /) -> int:
        return len(self._source)

    def __iter__(self, /) -> Iterator[_V]:
        return iter(self._source)

    def __contains__(self, value: _V, /) -> bool:
        return value in self._source


class BijectiveMap(Generic[_T1, _T2]):
    __slots__ = '_data'

    _no_arg: ClassVar[object] = object()

    def __init__(self, iterable: Iterable[_V] = (), /):
        self._data: dict[_K, _V] = {}
        for v1, v2 in iterable:
            self.update(v1, v2)

    def _add(self, v1: _T1, v2: _T2, /):
        t = v1, v2
        self._data[v1] = t
        self._data[v2] = t

    def add(self, v1: _T1, v2: _T2, /):
        if v1 in self._data:
            v = v1
        elif v2 in self._data:
            v = v2
        else:
            self._add(v1, v2)
            return

        raise ValueError(f'Value {v} is already bound to {self[v]}')

    def update(self, v1: _T1, v2: _T2, /):
        if v1 in self._data:
            self.__delitem__(v1)
        if v2 in self._data:
            self.__delitem__(v2)
        self._add(v1, v2)

    @overload
    def get(self, value: _T1, /) -> _T2: ...

    @overload
    def get(self, value: _T2, /) -> _T1: ...

    @overload
    def get(self, value: _T1, default: _T2, /) -> _T2: ...

    @overload
    def get(self, value: _T2, default: _T1, /) -> _T1: ...

    def get(self, value: _K, default: _K = _no_arg, /) -> _K:
        v1, v2 = self._data[value]
        if value is v1 or value == v1:
            return v2

        if value is v2 or value == v2:
            return v1

        if default is self._no_arg:
            raise KeyError(f'Key {value} points to tuple ({v1}, {v2}) which does not contain it')

        return default

    @overload
    def __getitem__(self, value: _T1, /) -> _T2: ...

    @overload
    def __getitem__(self, value: _T2, /) -> _T1: ...

    def __getitem__(self, value: _K, /) -> _K:
        return self.get(value)

    @overload
    def pop(self, value: _T1, /) -> _T2: ...

    @overload
    def pop(self, value: _T2, /) -> _T1: ...

    @overload
    def pop(self, value: _T1, default: _T2, /) -> _T2: ...

    @overload
    def pop(self, value: _T2, default: _T1, /) -> _T1: ...

    def pop(self, value: _K, default: _K = _no_arg, /) -> _K:
        v = self.get(value, default)
        self.__delitem__(v)
        return v

    def popitem(self, /) -> _V:
        value, (v1, v2) = self._data.popitem()
        if value is v1 or value == v1:
            del self._data[v2]
        elif value is v2 or value == v2:
            del self._data[v1]

        return v1, v2

    def __delitem__(self, value: _K, /):
        v1, v2 = self._data[value]
        if value is v1 or value == v1 or value is v2 or value == v2:
            del self._data[v1]
            del self._data[v2]
        else:
            raise KeyError(f'Key {value} points to tuple ({v1}, {v2}) which does not contain it')

    def __len__(self, /) -> int:
        return len(self._data) // 2

    def __contains__(self, item: _V, /) -> bool:
        v1, v2 = item
        return v1 in self._data and v2 in self._data

    # Not possible to integrate this method into __contains__
    # _T1 or _T2 can be tuples of size 2
    # In such case, it is not possible to determine
    # whether _K or _V is passed
    def has_value(self, value: _K, /) -> bool:
        return value in self._data

    def __iter__(self, /) -> Iterator[_V]:
        visited = set()
        for item in self._data.items():
            if item in visited:
                continue

            visited.add(item)
            yield item

    def values(self, /) -> BijectiveMapValuesView[_K]:
        return BijectiveMapValuesView(self)

    def items(self, /) -> BijectiveMapItemsView[_V]:
        return BijectiveMapItemsView(self)

    def clear(self, /):
        self._data.clear()

    def __eq__(self, other, /) -> bool:
        if isinstance(other, self.__class__):
            return self._data == other._data

        return False

    def __ne__(self, other, /) -> bool:
        if isinstance(other, self.__class__):
            return self._data != other._data

        return False

    def __repr__(self, /):
        entries = ', '.join(repr(v) for v in self)
        return f'{self.__class__.__name__}[{entries}]'
