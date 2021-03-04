from collections.abc import Iterable, Iterator
from io import StringIO
from typing import Final, final

from .storage import wtsStorage
from .string import wtsString


@final
class wtsParsingError(Exception):
    __module__ = 'builtins'


def parse_lines(lines: Iterable[str], /) -> Iterator[wtsString]:
    id_ = 0
    comment = StringIO()
    content = StringIO()
    outside = True  # outside of content block
    for line in lines:
        if outside:
            if line.startswith('{'):
                outside = False
            elif line.startswith('// '):
                comment.write(line)
            elif line.startswith('STRING '):
                id_ = int(line.strip()[7:])
        elif line.startswith('}'):
            if id_ <= 0:
                raise wtsParsingError(f'Cannot create {wtsString.__name__} with non-positive id {id_}')
            if content.tell() == 0:
                raise wtsParsingError(f'Cannot create {wtsString.__name__} with empty content')

            yield wtsString(id_, comment.getvalue(), content.getvalue())

            id_ = 0
            # Why recreating is better https://stackoverflow.com/a/4330829
            comment = StringIO()
            content = StringIO()
            outside = True
        else:
            content.write(line)


@final
class wtsFile:
    __slots__ = '_filepath', '_storage'

    encoding: Final[str] = 'utf-8-sig'

    @classmethod
    def parse(cls, filepath: str, /) -> Iterator[wtsString]:
        with open(filepath, 'r', encoding=cls.encoding) as f:
            return parse_lines(f)

    def __init__(self, filepath: str, /):
        self._storage = wtsStorage(self.parse(filepath))
        self._filepath = filepath

    @property
    def filepath(self, /):
        return self._filepath

    @property
    def storage(self, /):
        return self._storage

    @storage.setter
    def storage(self, value: wtsStorage, /):
        self._storage = value

    def save_as(self, filepath: str, /):
        with open(filepath, 'w', encoding=self.encoding) as f:
            f.writelines(str(s) for s in self._storage)

    def save(self, /):
        self.save_as(self._filepath)

    def reset(self, /):
        self._storage = wtsStorage(self.parse(self._filepath))
