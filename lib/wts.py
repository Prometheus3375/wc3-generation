"""

TODO

Сделать класс wtsStorage, который парсит .wts файл и извлекает из него строки, а также будет иметь методы по поиску
и сохранению в файл.

Сделать все возможные строки в РО в тестовой карте и пропарсить полученный .wts на наличие новых типов и полей

"""
from enum import Enum
from io import StringIO
from typing import ClassVar, Iterator, final, overload


@final
class wtsString:
    __slots__ = 'id', 'comment', 'content'

    def __init__(self, id_: int, comment: str, content: str):
        self.id = id_
        self.comment = comment
        self.content = content

    def __str__(self):
        return (
            f'STRING {self.id}\n'
            f'{self.comment}'
            '{\n'
            f'{self.content}'
            '}\n\n'
        )


@final
class CommentType(Enum):
    Ability = 'Abilities'
    Item = 'Items'
    Unit = 'Units'
    Upgrade = 'Upgrades'


@final
class CommentField(Enum):
    EditorSuffix = 'EditorSuffix'
    Hotkey = 'Hotkey'
    Name = 'Name'
    Propernames = 'Propernames'
    Tip = 'Tip'
    Ubertip = 'Ubertip'
    Unhotkey = 'Unhotkey'
    Untip = 'Untip'
    Unubertip = 'Unubertip'


@final
class wtsFile:
    __slots__ = '_filepath', '_strings'

    encoding: ClassVar[str] = 'utf-8-sig'

    def __init__(self, filepath: str):
        self._filepath = filepath
        self._strings: list[wtsString] = []

    def read(self):
        self._strings.clear()
        id_ = -1
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
                    self._strings.append(wtsString(id_, comment.getvalue(), content.getvalue()))
                    id_ = -1
                    # Why recreating better https://stackoverflow.com/a/4330829
                    comment = StringIO()
                    content = StringIO()
                    outside = True
                else:
                    content.write(line)

        return self

    def save(self):
        with open(self._filepath, 'w', encoding=self.encoding) as f:
            f.writelines(str(s) for s in self._strings)

    @property
    def filepath(self) -> str:
        return self._filepath

    def __len__(self) -> int:
        return len(self._strings)

    def __contains__(self, item: wtsString) -> bool:
        return item in self._strings

    def __iter__(self) -> Iterator[wtsString]:
        return iter(self._strings)

    @overload
    def __getitem__(self, index: int) -> wtsString: ...

    @overload
    def __getitem__(self, slice_: slice) -> list[wtsString]: ...

    def __getitem__(self, item):
        return self._strings[item]
