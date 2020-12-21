from traceback import format_tb
from typing import Any, Callable


def except_(smth: Callable[..., Any], *args, **kwargs):
    try:
        return smth(*args, **kwargs)
    except Exception as e:
        message = ''.join(format_tb(e.__traceback__))
        message = f'Traceback (most recent call last):\n{message}{e.__class__.__name__}: {e}\n'
        print(message)
