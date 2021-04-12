from collections.abc import Iterable, Iterator
from io import StringIO
from typing import Final, Optional, Union, final

from .string import _CommentData, wtsCommentField, wtsCommentType, wtsString


@final
class wtsStorageError(Exception):
    __module__ = 'builtins'


@final
class _CommentMap:
    __slots__ = '_map',

    def __init__(self, /):
        self._map: dict[_CommentData, list[wtsString]] = {}

    def __len__(self, /) -> int:
        return len(self._map)

    def __contains__(self, item: _CommentData, /) -> bool:
        return item in self._map

    def __iter__(self, /) -> Iterator[_CommentData]:
        return iter(self._map)

    def __getitem__(self, item: _CommentData, /) -> Optional[list[wtsString]]:
        return self._map.get(item)

    def add(self, wts: wtsString, /) -> bool:
        data = wts.comment_data
        if data:
            if data in self._map:
                self._map[data].append(wts)
            else:
                self._map[data] = [wts]

            return True

        return False

    def remove(self, wts: wtsString, /) -> bool:
        data = wts.comment_data
        if data:
            record = self._map.get(data)
            if record is None:
                raise wtsStorageError(f'cannot remove comment data for {wts!r}, '
                                      f'its data is not present in the comment map')

            try:
                record.remove(wts)
            except ValueError:
                raise wtsStorageError(f'cannot remove comment data for {wts!r}, '
                                      f'its is not present in the comment map') from None

            if len(record) == 0:
                del self._map[data]

            return True

        return False

    def clear(self, /):
        self._map.clear()


def parse_lines(lines: Iterable[str], /) -> Iterator[wtsString]:
    id = -1
    comment = StringIO()
    content = StringIO()
    outside = True  # outside of content block
    for line in lines:
        if outside:
            if line.startswith('STRING '):
                id = int(line.strip()[7:])
            elif id != -1:
                if line.startswith('// '):
                    comment.write(line)
                elif line.startswith('{'):
                    outside = False
        elif line.startswith('}'):
            yield wtsString(id, content.getvalue(), comment.getvalue())

            id = -1
            # Why recreating is better https://stackoverflow.com/a/4330829
            comment = StringIO()
            content = StringIO()
            outside = True
        else:
            content.write(line)


@final
class wtsStorage:
    __slots__ = '_strings', '_comment_map', '_free_indexes'

    file_encoding: Final[str] = 'utf-8-sig'

    def __init__(self, strings: Iterable[wtsString] = (), /):
        self._strings: dict[int, wtsString] = {}
        self._comment_map = _CommentMap()
        for wts in strings:
            if wts.id in self._strings:
                raise wtsStorageError(f'id repeated: {self._strings[wts.id]!r} and {wts!r}')

            self._add_string(wts)

        ids = self._strings.keys()
        max_id = max(ids)
        indexes = [max_id + 1]

        if max_id > len(self._strings):
            for i in range(max_id - 1, 0, -1):
                if i not in ids:
                    indexes.append(i)

        self._free_indexes = indexes

    def __len__(self, /) -> int:
        return len(self._strings)

    def __contains__(self, item: Union[int, wtsString], /) -> bool:
        if isinstance(item, int):
            return item in self._strings

        if isinstance(item, wtsString):
            return self._strings.get(item.id, None) is item

        return False

    def __iter__(self, /) -> Iterator[wtsString]:
        return iter(self._strings.values())

    def __getitem__(self, id: int, /) -> wtsString:
        return self._strings[id]

    def _add_string(self, wts: wtsString, /):
        self._strings[wts.id] = wts
        self._comment_map.add(wts)

    def add(self, content: str, comment: str = '', /) -> wtsString:
        id = self._free_indexes.pop()
        if len(self._free_indexes) == 0:
            self._free_indexes.append(id + 1)

        wts = wtsString(id, content, comment)
        self._add_string(wts)
        return wts

    def __delitem__(self, id: int, /):
        wts = self._strings.pop(id)
        if id > 0:
            self._free_indexes.append(id)
            self._comment_map.remove(wts)

    def clear(self, /):
        self._strings.clear()
        self._comment_map.clear()
        self._free_indexes = [1]

    def find(self, typ: wtsCommentType, rawcode: str, field: wtsCommentField, /, level: int = 1) -> Optional[wtsString]:
        # If a string is changed in the editor, old string is removed, a new is appended to the end
        # This breaks the order of multilevel strings
        # It is possible to fix by using autofill on all levels
        strings = self._comment_map[typ, rawcode, field]
        if strings is None:
            return None

        return strings[level - 1]

    @classmethod
    def open(cls, filepath: str, /):
        with open(filepath, 'r', encoding=cls.file_encoding) as f:
            return cls(parse_lines(f))

    def save(self, filepath: str, /):
        with open(filepath, 'w', encoding=self.file_encoding) as f:
            f.writelines(str(wts) for wts in sorted(self._strings.values()))
