from collections.abc import Iterable, Iterator
from typing import Optional, Union, final

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
        return iter(self._map)

    def clear(self, /):
        self._map.clear()


@final
class wtsStoringError(Exception):
    __module__ = 'builtins'


@final
class wtsStorage:
    __slots__ = '_strings', '_comment_map'

    def __init__(self, strings: Iterable[wtsString] = (), /):
        self._strings: dict[int, wtsString] = {}
        self._comment_map = CommentMap()
        for wts in strings:
            if wts.id in self._strings:
                raise wtsStoringError(f'id repeated: {self._strings[wts.id]!r} and {wts!r}')

            self._strings[wts.id] = wts
            self._comment_map.add(wts)

    def __len__(self, /) -> int:
        return len(self._strings)

    def __contains__(self, item: Union[int, wtsString], /) -> bool:
        if isinstance(item, int):
            return item in self._strings

        if isinstance(item, wtsString):
            return self._strings.get(item.id, None) is item

        return False

    def __iter__(self, /) -> Iterator[wtsString]:
        return iter(sorted(self._strings.values()))

    def __getitem__(self, id_: int, /) -> wtsString:
        return self._strings[id_]

    def find(self, typ: CommentType, rawcode: str, field: CommentField, /, level: int = 1) -> Optional[wtsString]:
        # If a string is changed in the editor, old string is removed, a new is appended to the end
        # This breaks the order of multilevel strings
        # It is possible to fix by using autofill on all levels
        strings = self._comment_map[typ, rawcode, field]
        if strings is None:
            return None

        return strings[level - 1]
