from enum import Enum
from typing import Optional, final

from misclib import truncate_string


@final
class wtsCommentType(Enum):
    Ability = 'Abilities'
    BuffEffect = 'Buffs/Effects'
    Destructible = 'Destructibles'
    Doodad = 'Doodads'
    Item = 'Items'
    Unit = 'Units'
    Upgrade = 'Upgrades'


@final
class wtsCommentField(Enum):
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


_CommentData = tuple[wtsCommentType, str, wtsCommentField]


class wtsStringError(Exception):
    __module__ = 'builtins'


@final
class wtsString:
    __slots__ = '_id', '_comment', '_content'

    def __init__(self, id: int, content: str, comment: str = '', /):
        if id < 0:
            raise wtsStringError(f'id cannot be negative, got {id}')

        self._id = id
        self._comment = comment
        self._content = content

    @property
    def id(self, /) -> int:
        return self._id

    @property
    def comment(self, /) -> str:
        return self._comment

    @property
    def comment_data(self, /) -> Optional[_CommentData]:
        comment = self._comment.strip()
        if not comment:
            return None

        colon = comment.index(':')
        typ = wtsCommentType(comment[3:colon])
        rawcode = comment[colon + 2:colon + 6]
        closing_brace = comment.rindex(')', colon + 8, len(comment) - 2)
        opening_brace = comment.index('(', closing_brace + 3)
        field = wtsCommentField(comment[closing_brace + 3:opening_brace - 1])
        return typ, rawcode, field

    @property
    def content(self, /):
        return self._content

    @content.setter
    def content(self, value: str, /):
        self._content = value

    def __str__(self, /) -> str:
        return (
            f'STRING {self.id}\n'
            f'{self._comment}'
            '{\n'
            f'{self._content}'
            '}\n\n'
        )

    def __repr__(self, /) -> str:
        return (
            f'{self.__class__.__name__}('
            f'id={self._id}, '
            f'comment={truncate_string(self._comment[3:].strip())!r}, '
            f'content={truncate_string(self._content.strip())!r}'
            f')'
        )

    def __lt__(self, other: object, /):
        if isinstance(other, self.__class__):
            return self._id < other._id

        return NotImplemented
