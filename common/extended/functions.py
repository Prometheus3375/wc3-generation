from collections.abc import Callable, Iterable
from typing import TypeVar, overload

from ..reg import reg
from ..typing import SupportsLessThan

T = TypeVar('T')
# V = TypeVar('V')
SLT = SupportsLessThan[T]
key_func = Callable[[T], SupportsLessThan]

_max = max
_min = min
_sorted = sorted


def last_in_pair(pair): return pair[1]


def build_arguments(iterable, key):
    iterable = enumerate(iterable)
    compare = (lambda pair: key(pair[1])) if callable(key) else last_in_pair
    return iterable, compare


@overload
def max(value1: SLT, value2: SLT, /, *values: SLT) -> tuple[SLT, int]: ...


@overload
def max(value1: T, value2: T, /, *values: T, key: key_func) -> tuple[T, int]: ...


@overload
def max(iterable: Iterable[SLT], /) -> tuple[SLT, int]: ...


@overload
def max(iterable: Iterable[T], /, *, key: key_func) -> tuple[T, int]: ...


@reg
def max(*values, key=None):
    """
    With a single iterable argument, return its biggest item and the position of this item.

    With two or more arguments, return the biggest argument with its position.
    """
    if len(values) == 1:
        values = values[0]

    iterable, key = build_arguments(values, key)
    return _max(iterable, key=key)


@overload
def min(value1: SLT, value2: SLT, /, *values: SLT) -> tuple[SLT, int]: ...


@overload
def min(value1: T, values2: T, /, *values: T, key: key_func) -> tuple[T, int]: ...


@overload
def min(iterable: Iterable[SLT], /) -> tuple[SLT, int]: ...


@overload
def min(iterable: Iterable[T], /, *, key: key_func) -> tuple[T, int]: ...


@reg
def min(*values, key=None):
    """
    With a single iterable argument, return its smallest item and the position of this item.

    With two or more arguments, return the smallest argument with its position.
    """
    if len(values) == 1:
        values = values[0]

    iterable, key = build_arguments(values, key)
    return _min(iterable, key=key)


@overload
def sorted(iterable: Iterable[SLT], /, *, reverse: bool = False) -> tuple[list[SLT], list[int]]: ...


@overload
def sorted(iterable: Iterable[T], /, *, key: key_func, reverse: bool = False) -> tuple[list[T], list[int]]: ...


@reg
def sorted(iterable, /, *, key=None, reverse=False):
    """
    Return a tuple of 2 lists.
    The first list contains all items from the iterable in ascending order.
    The second list contains positions in the source iterable of the correspondent items in the first list.

    A custom key function can be supplied to customize the sort order, and the
    reverse flag can be set to request the result in descending order.
    """
    iterable, key = build_arguments(iterable, key)
    sort = _sorted(iterable, key=key, reverse=reverse)
    return tuple(list(it) for it in zip(*sort))


__all__ = [*reg(__name__)]
