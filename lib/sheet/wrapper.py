from collections.abc import Iterator
from typing import Union, final

from gspread import Spreadsheet, Worksheet

_K = Union[int, str]


@final
class SpreadsheetWrapper:
    __slots__ = '_source', '_sheets_', '_not_fetched'

    __instances__: dict[str, 'SpreadsheetWrapper'] = {}

    def __new__(cls, sh: Spreadsheet, /):
        instance = cls.__instances__.get(sh.id, None)
        if instance:
            return instance

        instance = object.__new__(cls)
        instance._source = sh
        # noinspection PyTypeHints
        instance._sheets_: dict[_K, Worksheet] = {}
        instance._not_fetched = True
        cls.__instances__[sh.id] = instance

        return instance

    @property
    def source(self, /):
        return self._source

    def refetch(self, /):
        self._sheets_.clear()
        for i, sheet in enumerate(self._source.worksheets()):
            self._sheets_[i] = self._sheets_[sheet.title.lower()] = sheet
        # noinspection PyAttributeOutsideInit
        self._not_fetched = False

    @classmethod
    def refetch_all(cls, /):
        for wrapper in cls.__instances__.values():
            wrapper.refetch()

    @property
    def _sheets(self, /):
        if self._not_fetched:
            self.refetch()
        return self._sheets_

    def __len__(self, /) -> int:
        return len(self._sheets) // 2

    def __iter__(self, /) -> Iterator[Worksheet]:
        return (value for key, value in self._sheets.items() if isinstance(key, int))

    def get(self, key: _K) -> Union[Worksheet, None]:
        return self._sheets.get(key, None)

    def __contains__(self, item: _K, /) -> bool:
        return item in self._sheets

    def __getitem__(self, item: _K, /) -> Worksheet:
        return self._sheets[item]

    def __repr__(self, /) -> str:
        return f'{self.__class__.__name__}{self._source}'
