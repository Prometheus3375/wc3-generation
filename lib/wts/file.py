from collections.abc import Iterator
from io import StringIO
from typing import ClassVar, Optional, final

from .string import CommentData, CommentField, CommentType, wtsString


@final
class CommentMap:
    __slots__ = '_map',

    def __init__(self, /):
        self._map: dict[CommentData, list[wtsString]] = {}

    def add(self, value: wtsString, /) -> bool:
        data = value.comment_data
        if data:
            if data in self._map:
                self._map[data].append(value)
            else:
                self._map[data] = [value]

            return True

        return False

    def __getitem__(self, item: CommentData, /) -> Optional[list[wtsString]]:
        return self._map.get(item, None)

    def __len__(self, /) -> int:
        return len(self._map)

    def __contains__(self, item: CommentData, /) -> bool:
        return item in self._map

    def __iter__(self, /) -> Iterator[CommentData]:
        yield from self._map

    def clear(self, /):
        self._map.clear()


@final
class wtsReadError(Exception):
    __module__ = 'builtins'


@final
class wtsFile:
    __slots__ = '_filepath', '_strings', '_comment_map'

    encoding: ClassVar[str] = 'utf-8-sig'

    def __init__(self, filepath: str, /):
        self._filepath = filepath
        self._strings: dict[int, wtsString] = {}
        self._comment_map = CommentMap()

    @property
    def filepath(self, /) -> str:
        return self._filepath

    def __len__(self, /) -> int:
        return len(self._strings)

    def __contains__(self, wts: wtsString, /) -> bool:
        return wts.id in self._strings and self._strings[wts.id] is wts

    def has_id(self, id_: int, /) -> bool:
        return id_ in self._strings

    def __iter__(self, /) -> Iterator[wtsString]:
        yield from sorted(self._strings.values())

    def __getitem__(self, id_: int, /) -> wtsString:
        return self._strings[id_]

    def read(self, /):
        self._strings.clear()
        self._comment_map.clear()
        id_ = 0
        comment = StringIO()
        content = StringIO()
        outside = True  # outside of content block
        with open(self._filepath, 'r', encoding=self.encoding) as f:
            for line in f:
                if outside:
                    if line.startswith('{'):
                        outside = False
                    elif line.startswith('// '):
                        comment.write(line)
                    elif line.startswith('STRING '):
                        id_ = int(line.strip()[7:])
                elif line.startswith('}'):
                    if id_ <= 0:
                        raise wtsReadError(f'Cannot create {wtsString.__name__} with non-positive id: {id_}')
                    if content.tell() == 0:
                        raise wtsReadError(f'Cannot create {wtsString.__name__} with empty content')

                    wts = wtsString(id_, comment.getvalue(), content.getvalue())
                    self._strings[wts.id] = wts
                    self._comment_map.add(wts)

                    id_ = 0
                    # Why recreating is better https://stackoverflow.com/a/4330829
                    comment = StringIO()
                    content = StringIO()
                    outside = True
                else:
                    content.write(line)

        return self

    def save(self, /):
        with open(self._filepath, 'w', encoding=self.encoding) as f:
            f.writelines(str(s) for s in self)

    def find(self, typ: CommentType, rawcode: str, field: CommentField, /, level: int = 1) -> Optional[wtsString]:
        # Notes:
        # If a string is changed in the editor, old string is removed, a new is appended to the end
        # This breaks the order of multilevel strings
        # It is possible to fix by using autofill on all levels
        strings = self._comment_map[typ, rawcode, field]
        if strings is None:
            return None

        return strings[level - 1]
