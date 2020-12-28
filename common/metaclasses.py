from typing import final
from weakref import WeakKeyDictionary, WeakValueDictionary

_combined_metaclasses = WeakValueDictionary()


def combine(*classes: type):
    # Order of bases matters
    # (A, B) and (B, A) different base tuples which lead to different MRO
    # So combined classes of these bases are different
    if classes in _combined_metaclasses:
        return _combined_metaclasses[classes]

    cls = CombineMeta(
        '@'.join(
            f'({cls.__qualname__})' if cls.__bases__ in _combined_metaclasses
            else cls.__qualname__
            for cls in classes
        ),
        classes,
        {'__module__': None}
    )
    _combined_metaclasses[classes] = cls
    return cls


@final
class CombineMeta(type):
    """
    A metaclass that allows metaclass combination
    """
    # Original idea: https://stackoverflow.com/a/45873191
    combine = staticmethod(combine)

    def __matmul__(self, other):
        return combine(self, other)

    def __rmatmul__(self, other):
        return combine(other, self)

    def __init_subclass__(mcs, **kwargs):
        raise TypeError(f'type {CombineMeta.__name__} is not an acceptable base type')


class Singleton(type, metaclass=CombineMeta):
    # Use weak keys to automatically clean unused classes
    __instances__ = WeakKeyDictionary()

    def __call__(cls, *args, **kwargs):
        instances = cls.__class__.__instances__
        if cls not in instances:
            instances[cls] = super().__call__(*args, **kwargs)

        return instances[cls]


class SingletonWithInit(Singleton):
    __call_init__ = WeakKeyDictionary()

    def __new__(mcs, name: str, bases: tuple, namespace: dict, *, call_init: bool = False, **kwargs):
        if not isinstance(call_init, bool):
            raise TypeError(f'call_init argument must be bool, got {type(call_init)}')

        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        mcs.__call_init__[cls] = call_init
        return cls

    def __call__(cls, *args, **kwargs):
        instance = super().__call__(*args, **kwargs)
        if cls.__class__.__call_init__[cls]:
            instance.__init__(*args, **kwargs)

        return instance


class EmptySlotsByDefaults(type, metaclass=CombineMeta):
    def __new__(mcs, name: str, bases: tuple, namespace: dict, **kwargs):
        if '__slots__' not in namespace:
            namespace['__slots__'] = ()
        return super().__new__(mcs, name, bases, namespace, **kwargs)


class AllowInstantiation(type, metaclass=CombineMeta):
    __allow__ = WeakKeyDictionary()

    def __new__(mcs, name: str, bases: tuple, namespace: dict, *, allow_instances: bool = True, **kwargs):
        if not isinstance(allow_instances, bool):
            raise TypeError(f'allow_instances argument must be bool, got {type(allow_instances)}')

        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        mcs.__allow__[cls] = allow_instances
        return cls

    def __call__(cls, *args, **kwargs):
        if cls.__class__.__allow__[cls]:
            return super().__call__(*args, **kwargs)

        raise TypeError(f'class {cls.__class__.__qualname__} cannot be instantiated')
