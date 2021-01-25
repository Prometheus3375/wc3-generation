from collections.abc import Iterator, MutableSet
from typing import overload


# TODO: add a function that will process all __all__ and rewrite it

class All(MutableSet[str]):
    __slots__ = '_set',
    module2all: dict[str, 'All'] = {}

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
        return iter(All.module2all.pop(o))

    module = o.__module__
    instance = All.module2all.get(module, None)
    if instance is None:
        instance = All(module)
    instance.add(o.__name__)
    return o


__all__ = 'reg',
