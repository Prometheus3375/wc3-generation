from typing import final
from weakref import WeakKeyDictionary


def combine(*classes: type):
    return CombineMeta(''.join(cls.__name__ for cls in classes), classes, {})


@final
class CombineMeta(type):
    """
    A metaclass that allows metaclass combination
    """
    # Original idea: https://stackoverflow.com/a/45873191
    combine = staticmethod(combine)

    def __matmul__(self, other):
        return CombineMeta(self.__name__ + other.__name__, (self, other), {})

    def __rmatmul__(self, other):
        return CombineMeta(other.__name__ + self.__name__, (other, self), {})

    def __init_subclass__(mcs, **kwargs):
        raise TypeError(f'type MetaOfMeta is not an acceptable base type')


class Singleton(type, metaclass=CombineMeta):
    # Use weak keys to automatically clean unused classes
    __instances__ = WeakKeyDictionary()
    __call_init__ = WeakKeyDictionary()

    def __new__(mcs, name: str, bases: tuple, namespace: dict, *, call_init: bool = False):
        cls = super().__new__(mcs, name, bases, namespace)
        if not isinstance(call_init, bool):
            raise TypeError(f'call_init argument must be bool, got {type(call_init)}')

        mcs.__call_init__[cls] = call_init
        return cls

    def __call__(cls, *args, **kwargs):
        instances = cls.__class__.__instances__
        call_init = cls.__class__.__call_init__[cls]
        if cls not in instances:
            instances[cls] = super().__call__(cls, *args, **kwargs)
        elif call_init:
            instances[cls].__init__(*args, **kwargs)

        return instances[cls]


class EmptySlotsByDefaults(type, metaclass=CombineMeta):
    def __new__(mcs, name: str, bases: tuple, namespace: dict):
        if '__slots__' not in namespace:
            namespace['__slots__'] = ()
        return super().__new__(mcs, name, bases, namespace)
