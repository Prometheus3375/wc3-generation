from collections.abc import ItemsView, Iterable, Iterator, KeysView, Mapping, ValuesView
from itertools import chain
from sys import getsizeof
from typing import Generic, Optional, TypeVar, Union, overload

from .typing import SupportsKeysAndGetItem

_K_co = TypeVar('_K_co', covariant=True)
_V_co = TypeVar('_V_co', covariant=True)
_T = TypeVar('_T')
_S = TypeVar('_S')


@Mapping.register
class frozendict(Generic[_K_co, _V_co]):
    __slots__ = '_source', '_hash'

    @overload
    def __init__(self, /, **kwargs: _V_co): ...
    @overload
    def __init__(self, mapping: SupportsKeysAndGetItem[_K_co, _V_co], /, **kwargs: _V_co): ...
    @overload
    def __init__(self, iterable: Iterable[tuple[_K_co, _V_co]], /, **kwargs: _V_co): ...

    def __init__(self, iterable=(), /, **kwargs):
        self._source = dict(iterable, **kwargs)
        self._hash = hash(frozenset(self._source.items()))

    def __getitem__(self, item: _K_co, /) -> _V_co:
        return self._source[item]

    @overload
    def get(self, key: _K_co, /) -> Optional[_V_co]: ...
    @overload
    def get(self, key: _K_co, default: _V_co, /) -> _V_co: ...
    @overload
    def get(self, key: _K_co, default: _T, /) -> Union[_V_co, _T]: ...

    def get(self, key, default=None, /):
        return self._source.get(key, default)

    @classmethod
    @overload
    def fromkeys(cls, iterable: Iterable[_T], /) -> 'frozendict[_T, None]': ...
    @classmethod
    @overload
    def fromkeys(cls, iterable: Iterable[_T], value: _S, /) -> 'frozendict[_T, _S]': ...

    @classmethod
    def fromkeys(cls, iterable: Iterable, value=None, /):
        # noinspection PyArgumentList
        return cls((k, value) for k in iterable)

    def keys(self, /) -> KeysView[_K_co]:
        return self._source.keys()

    def values(self, /) -> ValuesView[_V_co]:
        return self._source.values()

    def items(self, /) -> ItemsView[_K_co, _V_co]:
        return self._source.items()

    def copy(self, /):
        # noinspection PyArgumentList
        return self.__class__(self._source)

    def __repr__(self, /):
        return f'{self.__class__.__name__}({self._source})'

    def __str__(self, /):
        return str(self._source)

    def __len__(self, /):
        return len(self._source)

    def __contains__(self, item, /):
        return item in self._source

    def __iter__(self, /) -> Iterator[_K_co]:
        return iter(self._source)

    def __reversed__(self, /) -> Iterator[_K_co]:
        return reversed(self._source)

    def __or__(self, other: Mapping[_K_co, _V_co], /) -> 'frozendict[_K_co, _V_co]':
        if isinstance(other, Mapping):
            # noinspection PyArgumentList
            return self.__class__(chain(self._source.items(), other.items()))

        return NotImplemented

    def __ror__(self, other: Mapping[_K_co, _V_co], /) -> 'frozendict[_K_co, _V_co]':
        if isinstance(other, Mapping):
            # noinspection PyArgumentList
            return self.__class__(chain(other.items(), self._source.items()))

        return NotImplemented

    def __eq__(self, other, /):
        return self._source == other

    def __ne__(self, other, /):
        return self._source != other

    def __hash__(self, /):
        return self._hash

    def __getnewargs__(self, /):
        return tuple(self.items())

    def __sizeof__(self):
        return object.__sizeof__(self) + getsizeof(self._source) + getsizeof(self._hash)


__all__ = [frozendict.__name__]
