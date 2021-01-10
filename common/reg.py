from collections.abc import Iterator, MutableSet
from typing import overload


class _All(MutableSet[str]):
    __slots__ = '_set',
    module2all: dict[str, '_All'] = {}

    def __init__(self, module: str):
        self._set = set()
        self.module2all[module] = self

    def add(self, name: str):
        self._set.add(name)

    def discard(self, name: str):
        self._set.discard(name)

    def __len__(self) -> int:
        return len(self._set)

    def __contains__(self, name: str) -> bool:
        return name in self._set

    def __iter__(self) -> Iterator[str]:
        return iter(sorted(self._set))


@overload
def reg(o: object) -> object: ...


@overload
def reg(module: str) -> Iterator[str]: ...


def reg(o: object):
    if isinstance(o, str):
        return iter(_All.module2all.pop(o))

    module = o.__module__
    instance = _All.module2all.get(module, None)
    if instance is None:
        instance = _All(module)
    instance.add(o.__name__)
    return o


__all__ = [reg.__name__]
