from collections.abc import ItemsView, Iterable, Iterator, KeysView, Mapping, ValuesView
from itertools import chain
from typing import Generic, TypeVar, Union, overload

from .typing import SupportsKeysAndGetItem

_K = TypeVar('_K')
_V_co = TypeVar('_V_co', covariant=True)
_T = TypeVar('_T')
_S = TypeVar('_S')


# noinspection PyArgumentList
class frozendict(Generic[_K, _V_co]):
    __slots__ = '_source', '_hash'
    _dummy = object()

    @overload
    def __init__(self, /, **kwargs: _V_co): ...
    @overload
    def __init__(self, map_: SupportsKeysAndGetItem, /, **kwargs: _V_co): ...
    @overload
    def __init__(self, iterable: Iterable[tuple[_K, _V_co]], /, **kwargs: _V_co): ...

    def __init__(self, iterable=(), /, **kwargs):
        self._source = dict(iterable, **kwargs)
        self._hash = hash(frozenset(self._source.items()))

    def __getitem__(self, item: _K, /) -> _V_co:
        return self._source[item]

    @overload
    def get(self, key: _K, /) -> _V_co: ...
    @overload
    def get(self, key: _K, default: Union[_V_co, _T], /) -> Union[_V_co, _T]: ...

    def get(self, key, default=_dummy, /):
        if default is self._dummy:
            return self._source.get(key)

        return self._source.get(key, default)

    @classmethod
    @overload
    def fromkeys(cls, iterable: Iterable[_T], /) -> 'frozendict[_T, None]': ...
    @classmethod
    @overload
    def fromkeys(cls, iterable: Iterable[_T], value: _S, /) -> 'frozendict[_T, _S]': ...

    @classmethod
    def fromkeys(cls, iterable: Iterable, value=None, /):
        return cls(tuple((k, value) for k in iterable))

    def keys(self, /) -> KeysView[_K, _V_co]:
        return self._source.keys()

    def values(self, /) -> ValuesView[_K, _V_co]:
        return self._source.values()

    def items(self, /) -> ItemsView[_K, _V_co]:
        return self._source.items()

    def copy(self, /):
        return self.__class__(self._source)

    def __repr__(self, /):
        return f'{self.__class__.__name__}({self._source})'

    def __str__(self, /):
        return str(self._source)

    def __len__(self, /):
        return len(self._source)

    def __contains__(self, item, /):
        return item in self._source

    def __iter__(self, /) -> Iterator[_K]:
        return iter(self._source)

    def __reversed__(self, /) -> Iterator[_K]:
        return reversed(self._source)

    def __or__(self, other: Mapping[_K, _V_co], /) -> 'frozendict[_K, _V_co]':
        return self.__class__(self._source | other)

    def __ror__(self, other: Mapping[_K, _V_co], /) -> Mapping[_K, _V_co]:
        return other.__class__(chain(other.items(), self._source.items()))

    def __eq__(self, other, /):
        return self._source == other

    def __ne__(self, other, /):
        return self._source != other

    def __hash__(self, /):
        return self._hash

    def __getnewargs__(self, /):
        return tuple(self.items())
