from collections.abc import Callable, Collection, Iterable, Sequence
from traceback import format_tb
from typing import Any, TypeVar, Union, overload

from .reg import reg
from .typing import SupportsLessThan

_T = TypeVar('_T')
_V = TypeVar('_V')
_IterableStr = Union[Iterable[str], str]


@reg
def exc2str(e: Exception) -> str:
    message = ''.join(format_tb(e.__traceback__))
    message = f'Traceback (most recent call last):\n{message}{e.__class__.__name__}: {e}\n'
    return message


@reg
def except_(smth: Callable[..., Any], *args, **kwargs):
    try:
        return smth(*args, **kwargs)
    except Exception as e:
        print(exc2str(e))


@reg
def isnamedtuplesubclass(cls: type) -> bool:
    # https://stackoverflow.com/a/2166841
    bases = cls.__bases__
    if len(bases) != 1 or bases[0] is not tuple:
        return False

    fields = getattr(cls, '_fields', None)
    if not isinstance(fields, tuple):
        return False

    return all(type(n) is str for n in fields)


@reg
def isnamedtuple(obj: tuple) -> bool:
    return isnamedtuplesubclass(obj.__class__)


@reg
def truncate_string(s: str, max_len: int = 10) -> str:
    return s if len(s) <= max_len else f'{s[:max_len - 3]}...'


@reg
def repr_collection(c: Collection, singular: _IterableStr, plural: _IterableStr, /, *,
                    delimiter: str = ', ', use_repr: bool = True) -> tuple[_IterableStr, str]:
    func = repr if use_repr else str
    return singular if len(c) == 1 else plural, delimiter.join(func(o) for o in c)


_SLT = SupportsLessThan[_T]
_key_func = Callable[[_T], SupportsLessThan]


# TODO: create module extensions and move there extended max, min, sorted
@reg
def identity(o):
    """
    Return the passed object unchanged.

    :param o: any object
    :return: passed object
    """
    return o


@overload
def max_ext(*v: _SLT) -> tuple[_SLT, int]: ...


@overload
def max_ext(*v: _T, key: _key_func) -> tuple[_T, int]: ...


@overload
def max_ext(iterable: Iterable[_SLT], /) -> tuple[_SLT, int]: ...


@overload
def max_ext(iterable: Iterable[_T], /, *, key: _key_func) -> tuple[_T, int]: ...


@reg
def max_ext(*args, key=None):
    if len(args) == 1:
        args = args[0]
        if not isinstance(args, Iterable):
            raise TypeError(f'{args.__class__.__name__!r} object is not iterable')

    compare = key if callable(key) else identity
    iter_ = iter(args)
    try:
        max_ = next(iter_)
    except StopIteration:
        raise ValueError(f'{max_ext.__name__}() argument is an empty sequence')
    max_comp = compare(max_)
    max_idx = 0
    for i, obj in enumerate(iter_, 1):
        obj_comp = compare(obj)
        if max_comp < obj_comp:
            max_ = obj
            max_comp = obj_comp
            max_idx = i

    return max_, max_idx


@reg
def first_in_sequence(c: Sequence[_T]) -> _T: return c[0]


@overload
def sorted_ext(iterable: Iterable[_SLT], /, *, reverse: bool = False) -> tuple[list[_SLT], list[int]]: ...


@overload
def sorted_ext(iterable: Iterable[_T], /, *, key: _key_func, reverse: bool = False) -> tuple[list[_T], list[int]]: ...


@reg
def sorted_ext(iterable, /, *, key=None, reverse=False):
    if not isinstance(iterable, Collection):
        iterable = tuple(iterable)

    iterable = zip(iterable, range(len(iterable)))
    key_ = (lambda x: key(x[0])) if callable(key) else first_in_sequence
    sort = sorted(iterable, key=key_, reverse=reverse)
    return tuple(list(it) for it in zip(*sort))


__all__ = [*reg(__name__)]
