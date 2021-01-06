"""
TODO

Report problem that pycharm suggest to import abc collections from collections
not from collections.abc.
Import from collections was deprecated since 3.3.
"""

from collections.abc import Callable, Collection, Iterable, Set
from traceback import format_tb
from typing import Any, Union

_IterableStr = Union[Iterable[str], str]


def exc2str(e: Exception) -> str:
    message = ''.join(format_tb(e.__traceback__))
    message = f'Traceback (most recent call last):\n{message}{e.__class__.__name__}: {e}\n'
    return message


def except_(smth: Callable[..., Any], *args, **kwargs):
    try:
        return smth(*args, **kwargs)
    except Exception as e:
        print(exc2str(e))


def isnamedtuplesubclass(cls: type) -> bool:
    # https://stackoverflow.com/a/2166841
    bases = cls.__bases__
    if len(bases) != 1 or bases[0] is not tuple:
        return False

    fields = getattr(cls, '_fields', None)
    if not isinstance(fields, tuple):
        return False

    return all(type(n) is str for n in fields)


def isnamedtuple(obj: tuple) -> bool:
    return isnamedtuplesubclass(obj.__class__)


def truncate_string(s: str, max_len: int = 10) -> str:
    return s if len(s) <= max_len else f'{s[:max_len - 3]}...'


def repr_collection(c: Collection, singular: _IterableStr, plural: _IterableStr, /, *,
                    delimiter: str = ', ', use_repr: bool = True) -> tuple[_IterableStr, str]:
    func = repr if use_repr else str
    return singular if len(c) == 1 else plural, delimiter.join(func(o) for o in c)


def set_mismatch_message(correct: Set, incorrect: Set, missing_msg: str, unexpected_msg: str,
                         singular: str, plural: str, /, *, delimiter: str = '; ') -> str:
    msg = []
    if set_ := correct - incorrect:
        noun, rep = repr_collection(set_, singular, plural)
        msg.append(f'{missing_msg} {noun} {rep}')
    if set_ := incorrect - correct:
        noun, rep = repr_collection(set_, singular, plural)
        msg.append(f'{unexpected_msg} {noun} {rep}')
    return delimiter.join(msg)
