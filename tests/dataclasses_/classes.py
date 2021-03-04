from dataclasses import dataclass
from typing import Any, NamedTuple

from uncommon import except_


@dataclass
class DataClass:
    field1: int
    field2: int = 0

    def method(self):
        return 'Hello, I 2 fields'

    def method2(self):
        return f'Hello, I 2 fields: {self.field1} and {self.field2}'


@dataclass(frozen=True)
class FrozenDataClass:
    field1: int
    field2: int = 0

    def method(self):
        return 'Hello, I 2 fields'

    def method2(self):
        return f'Hello, I 2 fields: {self.field1} and {self.field2}'


class NamedTupleSub(NamedTuple):
    field1: int
    field2: int = 0

    def method(self):
        return 'Hello, I 2 fields'

    def method2(self):
        return f'Hello, I 2 fields: {self.field1} and {self.field2}'


class Object:
    __slots__ = 'field1', 'field2'

    def __init__(self, field1: int, field2: int = 0):
        self.field1 = field1
        self.field2 = field2

    def method(self):
        return 'Hello, I 2 fields'

    def method2(self):
        return f'Hello, I 2 fields: {self.field1} and {self.field2}'


class ObjectNoSlots:
    def __init__(self, field1: int, field2: int = 0):
        self.field1 = field1
        self.field2 = field2

    def method(self):
        return 'Hello, I 2 fields'

    def method2(self):
        return f'Hello, I 2 fields: {self.field1} and {self.field2}'


class ImmutableObject:
    __slots__ = 'field1', 'field2'

    def __init__(self, field1: int, field2: int = 0):
        self.field1 = field1
        self.field2 = field2

    def __setattr__(self, key: str, value: Any):
        if hasattr(self, key):
            raise AttributeError(
                f'cannot assign {value} to attribute {key} '
                f'of immutable {self.__class__.__name__} instance'
            )

        super().__setattr__(key, value)

    def method(self):
        return 'Hello, I 2 fields'

    def method2(self):
        return f'Hello, I 2 fields: {self.field1} and {self.field2}'


class ImmutableObjectSuper:
    __slots__ = 'field1', 'field2'

    def __init__(self, field1: int, field2: int = 0):
        s = super()
        s.__setattr__('field1', field1)
        s.__setattr__('field2', field2)

    def __setattr__(self, key: str, value: Any):
        raise AttributeError(
            f'cannot assign {value} to attribute {key} '
            f'of immutable {self.__class__.__name__} instance'
        )

    def method(self):
        return 'Hello, I 2 fields'

    def method2(self):
        return f'Hello, I 2 fields: {self.field1} and {self.field2}'


class ImmutableObjectObject:
    __slots__ = 'field1', 'field2'

    def __init__(self, field1: int, field2: int = 0):
        object.__setattr__(self, 'field1', field1)
        object.__setattr__(self, 'field2', field2)

    def __setattr__(self, key: str, value: Any):
        raise AttributeError(
            f'cannot assign {value} to attribute {key} '
            f'of immutable {self.__class__.__name__} instance'
        )

    def method(self):
        return 'Hello, I 2 fields'

    def method2(self):
        return f'Hello, I 2 fields: {self.field1} and {self.field2}'


if __name__ == '__main__':
    data = ImmutableObject(1)
    except_(exec, 'data.field2 = 1', {'data': data})
    except_(exec, 'data.field3 = 1', {'data': data})
    data = FrozenDataClass(1)
    except_(exec, 'data.field2 = 1', {'data': data})
    data = DataClass(1)
    except_(exec, 'data.field3 = 1', {'data': data})
