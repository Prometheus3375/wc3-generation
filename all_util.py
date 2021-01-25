import os
import runpy
import sys
from collections.abc import Container, Iterator, MutableSet
from typing import Any, overload


class All(MutableSet[str]):
    __slots__ = '_set',
    module2all: dict[str, 'All'] = {}

    def __init__(self, module: str, /):
        self._set = set()
        self.module2all[module] = self

    def add(self, name: str, /):
        self._set.add(name)

    def discard(self, name: str, /):
        self._set.discard(name)

    def __len__(self, /) -> int:
        return len(self._set)

    def __contains__(self, name: str, /) -> bool:
        return name in self._set

    def __iter__(self, /) -> Iterator[str]:
        return iter(self._set)


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


def path2module(path: str) -> str:
    return os.path.splitext(path.replace('/', '.').replace('\\', '.'))[0]


def get_module(path: str) -> dict[str, Any]:
    path = path2module(path)
    existing = sys.modules.get(path)
    if existing is None:
        return runpy.run_module(path)

    return existing.__dict__


# TODO
# It should be a separate package
# Add the ability to remove all_util import and @reg
# Add the ability to specify __all__ container type
# Add rewriting __all__ if it is on the last line
# Make reg fake, i. e. it does nothing, generation is done while compiling
# Also add support for reg annotations to add constants to __all__
# Investigate how to automatically run this when pushing to main on GitLab/GitHub

def compute_all(file: str):
    module = get_module(file)
    if all_ := module.get('__all__'):
        with open(file, 'a') as f:
            all_ = ''.join(f'    {name!r},\n' for name in sorted(all_))
            f.write(f'# noinspection PyRedeclaration\n__all__ = (\n{all_})\n')


def compute_all_dir(directory: str,
                    allow_list: Container[str] = frozenset(),
                    deny_list: Container[str] = frozenset(),
                    extensions: Container[str] = frozenset(('.py',)),
                    process_subs: bool = False):
    if not os.path.exists(directory):
        raise ValueError(f'path {directory!r} does not exist')

    if allow_list and deny_list:
        allowed = lambda x: x in allow_list and x not in deny_list
    elif allow_list:
        allowed = lambda x: x in allow_list
    elif deny_list:
        allowed = lambda x: x not in deny_list
    else:
        allowed = lambda x: True

    for root, dirs, files in os.walk(directory):
        # Run init module
        init = f'{root}{os.path.sep}__init__.py'
        if os.path.isfile(init):
            get_module(init)

        for f in files:
            path = f'{root}{os.path.sep}{f}'
            name, ext = os.path.splitext(f)
            if ext in extensions and allowed(name) and allowed(path):
                compute_all(path)

        if not process_subs:
            break


__all__ = 'reg', 'compute_all', 'compute_all_dir'
