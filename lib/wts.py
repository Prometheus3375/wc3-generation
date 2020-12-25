"""

TODO

Зарепортить баг о сбросе настройки инспекций проекта.

Изменить информацию о lvl1 и посмотреть изменения

"""
from enum import Enum
from io import StringIO
from typing import ClassVar, Iterator, Optional, final

from common import truncate_string


@final
class CommentType(Enum):
    Ability = 'Abilities'
    BuffEffect = 'Buffs/Effects'
    Destructible = 'Destructibles'
    Doodad = 'Doodads'
    Item = 'Items'
    Unit = 'Units'
    Upgrade = 'Upgrades'


@final
class CommentField(Enum):
    # Abilities
    Researchhotkey = 'Researchhotkey'
    Researchtip = 'Researchtip'
    Researchubertip = 'Researchubertip'
    Unhotkey = 'Unhotkey'
    Untip = 'Untip'
    Unubertip = 'Unubertip'

    # Buffs/Effects
    Bufftip = 'Bufftip'
    Buffubertip = 'Buffubertip'
    EditorName = 'EditorName'

    # Heroes
    Awakentip = 'Awakentip'  # instant revive in Tavern
    Revivetip = 'Revivetip'  # revive in altar
    Propernames = 'Propernames'

    # Units
    Casterupgradename = 'Casterupgradename'
    Casterupgradetip = 'Casterupgradetip'

    # Common
    Description = 'Description'
    EditorSuffix = 'EditorSuffix'
    Hotkey = 'Hotkey'
    Name = 'Name'
    Tip = 'Tip'
    Ubertip = 'Ubertip'


CommentData = tuple[CommentType, str, CommentField]


@final
class wtsString:
    __slots__ = '_id', '_comment', '_content'

    def __init__(self, id_: int, comment: str, content: str):
        self._id = id_
        self._comment = comment
        self._content = content

    @property
    def id(self) -> int:
        return self._id

    @property
    def comment(self) -> str:
        return self._comment

    @property
    def comment_data(self) -> Optional[CommentData]:
        comment = self.comment.strip()
        if not comment:
            return None

        colon = comment.index(':')
        typ = CommentType(comment[3:colon])
        rawcode = comment[colon + 2:colon + 6]
        closing_brace = comment.rindex(')', colon + 8, len(comment) - 2)
        opening_brace = comment.index('(', closing_brace + 3)
        field = CommentField(comment[closing_brace + 3:opening_brace - 1])
        return typ, rawcode, field

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value: str):
        self._content = value

    def __str__(self) -> str:
        return (
            f'STRING {self.id}\n'
            f'{self.comment}'
            '{\n'
            f'{self.content}'
            '}\n\n'
        )

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'id={self._id}, '
            f'comment=\'{truncate_string(self._comment[3:].strip())}\', '
            f'content=\'{truncate_string(self._content.strip())}\''
            f')'
        )

    def __lt__(self, other: object):
        if isinstance(other, self.__class__):
            return self._id < other._id

        raise TypeError(f"'<' is not supported between instances "
                        f"of '{self.__class__.__name__}' and '{other.__class__.__name__}'")


@final
class CommentMap:
    __slots__ = '_map',

    def __init__(self):
        self._map: dict[CommentData, list[wtsString]] = {}

    def add(self, value: wtsString) -> bool:
        data = value.comment_data
        if data:
            if data in self._map:
                self._map[data].append(value)
            else:
                self._map[data] = [value]

            return True

        return False

    def __getitem__(self, item: CommentData) -> Optional[list[wtsString]]:
        return self._map.get(item, None)

    def __len__(self) -> int:
        return len(self._map)

    def __contains__(self, item: CommentData) -> bool:
        return item in self._map

    def __iter__(self) -> Iterator[CommentData]:
        return iter(self._map)

    def clear(self):
        self._map.clear()


@final
class wtsReadError(Exception):
    __module__ = 'builtins'


@final
class wtsFile:
    __slots__ = '_filepath', '_strings', '_comment_map'

    encoding: ClassVar[str] = 'utf-8-sig'

    def __init__(self, filepath: str):
        self._filepath = filepath
        self._strings: dict[int, wtsString] = {}
        self._comment_map = CommentMap()

    @property
    def filepath(self) -> str:
        return self._filepath

    def __len__(self) -> int:
        return len(self._strings)

    def __contains__(self, wts: wtsString) -> bool:
        return wts.id in self._strings and self._strings[wts.id] is wts

    def has_id(self, id_: int) -> bool:
        return id_ in self._strings

    def __iter__(self) -> Iterator[wtsString]:
        return iter(sorted(self._strings.values()))

    def __getitem__(self, id_: int) -> wtsString:
        return self._strings[id_]

    def read(self):
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

    def save(self):
        with open(self._filepath, 'w', encoding=self.encoding) as f:
            f.writelines(str(s) for s in self)

    def find(self, typ: CommentType, rawcode: str, field: CommentField, level: int = 1) -> Optional[wtsString]:
        strings = self._comment_map[typ, rawcode, field]
        if strings is None:
            return None

        return strings[level - 1]
