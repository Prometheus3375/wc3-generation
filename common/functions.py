from collections.abc import Callable, Collection, Iterable
from traceback import format_tb
from typing import Any, Union

from all_util import reg

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


__all__ = *reg(__name__),
