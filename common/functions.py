from traceback import format_tb
from typing import Any, Callable


def except_(smth: Callable[..., Any], *args, **kwargs):
    try:
        return smth(*args, **kwargs)
    except Exception as e:
        message = ''.join(format_tb(e.__traceback__))
        message = f'Traceback (most recent call last):\n{message}{e.__class__.__name__}: {e}\n'
        print(message)


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
