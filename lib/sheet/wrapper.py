from collections.abc import Iterator
from typing import Union, final

from gspread import Spreadsheet as Sh, Worksheet


@final
class SpreadsheetWrapper:
    __instances__: dict[str, 'SpreadsheetWrapper'] = {}

    def __init__(self, sh: Sh, /):
        if sh.id not in self.__instances__:
            self._source = sh
            self._sheets: dict[Union[int, str], Worksheet] = {}
            self._not_fetched = True
            self.__instances__[sh.id] = self

    def __new__(cls, sh: Sh, /):
        instance = cls.__instances__.get(sh.id, None)
        if instance is None:
            return super().__new__(cls)

        return instance

    @property
    def source(self, /):
        return self._source

    def refetch(self, /):
        self._sheets.clear()
        for i, sheet in enumerate(self._source.worksheets()):
            self._sheets[i] = self._sheets[sheet.title] = sheet
        self._not_fetched = False

    @classmethod
    def refetch_all(cls, /):
        for wrapper in cls.__instances__.values():
            wrapper.refetch()

    def _fetch(self, /):
        if self._not_fetched:
            self.refetch()

        return self

    def __len__(self, /) -> int:
        return len(self._sheets) // 2

    def __iter__(self, /) -> Iterator[Worksheet]:
        return (value for key, value in self._fetch()._sheets.items() if isinstance(key, int))

    def __contains__(self, item: Union[int, str], /) -> bool:
        return item in self._fetch()._sheets

    def __getitem__(self, item: Union[int, str], /) -> Worksheet:
        return self._fetch()._sheets[item]

    def __repr__(self, /) -> str:
        return f'{self.__class__.__name__}{self._source}'
