"""

TODO

Иметь абстрактный  класс для листов с методами на извлечение строки, ряда, отдельной ячейки и т. п. При определении
подкласса делать проверки для требуемых полей. Для создания объекта будет передаваться матрица, которая при
необходимости будет транспонирована. Будут проверены названия колонок и их количество. После этого каждый ряд будет
прочитан, его значения будут сконвертированы в нужный тип и переданы в класс-ряд (именованный кортеж). При ошибке
конвертации выдавать ячейку, в которой произошла ошибка.

"""
from collections.abc import Iterator, Sequence
from typing import ClassVar, Generic, Optional, TypeVar, final
from weakref import WeakKeyDictionary

from gspread import Spreadsheet, Worksheet

from common import repr_collection
from common.metaclasses import EmptySlotsByDefaults
from .functions import _index2column
from .row import Row
from .wrapper import SpreadsheetWrapper


class _SheetMeta(EmptySlotsByDefaults):
    __instances__ = WeakKeyDictionary()

    def __call__(cls, /, *, refetch: bool = False):
        if cls is Sheet:
            raise TypeError(f'class {cls.__name__} cannot be instantiated')

        instances = cls.__class__.__instances__
        if refetch or cls not in instances:
            instances[cls] = super().__call__(refetch=refetch)

        return instances[cls]


@final
class SheetDefinitionError(Exception):
    __module__ = 'builtins'  # https://stackoverflow.com/a/19419825


@final
class SheetIdentificationError(Exception):
    __module__ = 'builtins'


@final
class SheetParsingError(Exception):
    __module__ = 'builtins'


_Row_co = TypeVar('_Row_co', covariant=True)


class Sheet(Generic[_Row_co], metaclass=_SheetMeta):
    spreadsheet: ClassVar[Spreadsheet]
    index: ClassVar[int]
    title: ClassVar[str]
    transpose: ClassVar[bool]
    row_class: ClassVar[type[Row]]

    __slots__ = '_rows',

    def __init__(self, /, *, refetch: bool = False):
        wrapper = SpreadsheetWrapper(self.spreadsheet)
        if refetch:
            wrapper.refetch()

        # region Evaluate appropriate sheet
        sheet_title: Optional[Worksheet] = None
        if self.title is not None:
            sheet_title = wrapper.get(self.title.lower())
            if sheet_title is None:
                raise SheetIdentificationError(f'spreadsheet {wrapper.source.title!r} does not have '
                                               f'sheet {self.title!r}')

        sheet_index: Optional[Worksheet] = None
        if self.index is not None:
            sheet_index = wrapper.get(self.index)
            if sheet_index is None:
                sheets = '1 sheet' if len(wrapper) == 1 else f'{len(wrapper)} sheets'
                raise SheetIdentificationError(f'spreadsheet {wrapper.source.title!r} has {sheets}, '
                                               f'got index {self.index}')

        if not (sheet_index is sheet_title or sheet_index is None or sheet_title is None):
            raise SheetIdentificationError(f'sheet number {self.index} has title {sheet_index.title!r}, '
                                           f'not {self.title!r}')

        # noinspection PyTypeChecker
        sheet: Worksheet = sheet_title if sheet_index is None else sheet_index
        # endregion

        self._rows = tuple(self.parse_values(sheet.get_all_values()))

    @classmethod
    def column(cls, index: int) -> str:
        if index <= 0:
            raise ValueError(f'column index must be positive, got {index}')

        if cls.transpose:
            return str(index)

        return _index2column(index)

    @classmethod
    def row(cls, index: int) -> str:
        if index <= 0:
            raise ValueError(f'row index must be positive, got {index}')

        if cls.transpose:
            return _index2column(index)

        return str(index)

    @classmethod
    def cell(cls, col: int, row: int) -> str:
        if cls.transpose:
            return f'{cls.row(row)}{cls.column(col)}'

        return f'{cls.column(col)}{cls.row(row)}'

    @classmethod
    def parse_values(cls, values: Sequence[Sequence[str]], /) -> Iterator[_Row_co]:
        columns = 'columns'
        if cls.transpose:
            values = list(zip(*values))
            columns = 'rows'

        # region Process names
        names: dict[str, int] = {}
        for i, name in enumerate(values[0], 1):
            name = name.strip().lower()
            if len(name) == 0:
                continue

            ins = names.setdefault(name, i)
            if ins != i:
                raise SheetParsingError(f'title repeated in {columns} {cls.column(i)} and {cls.column(ins)}')

        row_class: type[Row] = cls.row_class
        if (keys := names.keys()) != (titles := row_class.titles2conversions_.keys()):
            msg = []
            if set_ := titles - keys:
                noun, rep = repr_collection(set_, 'title', 'titles')
                msg.append(f'missing necessary {noun} {rep}')
            if set_ := keys - titles:
                noun, rep = repr_collection(set_, 'title', 'titles')
                msg.append(f'unexpected {noun} {rep}')
            msg = '; '.join(msg)
            raise SheetParsingError(f'in sheet {cls.__name__!r} {msg}')
        # endregion

        values = values[1:]
        for j, row in enumerate(values, 2):
            args = {}
            for name, i in names.items():
                value = row[i - 1].strip()
                convert = row_class.titles2conversions_[name]
                try:
                    value = convert(value)
                except Exception as e:
                    raise SheetParsingError(f'{e.__class__.__name__} at cell {cls.cell(i, j)}: {e}')

                args[name] = value

            yield row_class.from_titles_(args)

    def __init_subclass__(cls, /):
        if len(bases := cls.__bases__) != 1 or (len(bases) > 1 and bases[0] is not Sheet):
            raise TypeError(f'sheet must have only one base class and this class must be {Sheet.__name__!r}')

        fullname = f'{cls.__module__}.{cls.__qualname__}'

        # Check spreadsheet
        if hasattr(cls, 'spreadsheet'):
            if not isinstance(cls.spreadsheet, Spreadsheet):
                raise SheetDefinitionError(f'{fullname}.spreadsheet must be instance of {Spreadsheet}, '
                                           f'got {type(cls.spreadsheet)}')
        else:
            raise SheetDefinitionError(f'sheet {fullname} does not have spreadsheet')

        # region Check index and title
        has_index = hasattr(cls, 'index')
        if has_index:
            if type(cls.index) is not int:
                raise SheetDefinitionError(f'{fullname}.index must be integer, got {type(cls.index)}')
            elif cls.index < 0:
                raise SheetDefinitionError(f'{fullname}.index must be non-negative integer, got {cls.index}')
        else:
            cls.index = None

        if hasattr(cls, 'title'):
            if type(cls.title) is not str:
                raise SheetDefinitionError(f'{fullname}.title must be string, got {type(cls.title)}')
            elif len(cls.title) == 0:
                raise SheetDefinitionError(f'{fullname}.title must not be empty')
        elif has_index:
            cls.title = None
        else:
            cls.title = cls.__name__
        # endregion

        # Get transpose value
        if hasattr(cls, 'transpose'):
            if not isinstance(cls.transpose, bool):
                raise SheetDefinitionError(f'sheet {fullname} has non-bool value in transpose attribute')
        else:
            cls.transpose = False

        # region Extract and check row container class
        if hasattr(cls, '__orig_bases__'):
            cls.row_class = cls.__orig_bases__[0].__args__[0]
        elif not hasattr(cls, 'row_class'):
            raise SheetDefinitionError(f'sheet {fullname} does not have row container class; '
                                       f'specify row container class when subclassing, i. e. '
                                       f'class YourSheet(Sheet[YourRowContainer])')

        if not isinstance(cls.row_class, type):
            raise SheetDefinitionError(f'sheet {fullname} has non-class row container, '
                                       f'its type is {type(cls.row_class)}')

        if not issubclass(cls.row_class, Row):
            raise SheetDefinitionError(f'row container must be subclass of {Row.__name__}, '
                                       f'got {cls.row_class} for sheet {fullname}')
        # endregion
