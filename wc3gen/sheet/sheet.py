from collections.abc import Iterator, Sequence
from typing import Any, Generic, Optional, TypeVar, final, overload
from weakref import WeakKeyDictionary

from gspread import Spreadsheet, Worksheet

from misclib.functions import repr_collection
from misclib.metaclasses import EmptySlots
from .functions import _index2column
from .row import Row
from .wrapper import SpreadsheetWrapper


class _SheetMeta(EmptySlots):
    __instances__ = WeakKeyDictionary()
    spreadsheet: Spreadsheet
    index: Optional[int]
    title: Optional[str]
    transpose: bool
    row_class: type[Row]
    ignored_columns: set[str]

    def __call__(cls, /, *, refetch: bool = False):
        if cls is Sheet:
            raise TypeError(f'class {cls.__name__} cannot be instantiated')

        instances = cls.__class__.__instances__
        if cls not in instances:
            instances[cls] = super().__call__(refetch=refetch)
        elif refetch:
            instances[cls].__init__(refetch=refetch)

        return instances[cls]

    def __str__(self, /) -> str:
        if self is Sheet:
            return super().__str__()

        name = self.index if self.title is None else self.title
        return f'<Sheet {name!r} of spreadsheet {self.spreadsheet.title!r}>'


@final
class SheetDefinitionError(Exception):
    __module__ = 'builtins'  # https://stackoverflow.com/a/19419825


@final
class SheetIdentificationError(Exception):
    __module__ = 'builtins'


@final
class SheetParsingError(Exception):
    __module__ = 'builtins'


def _fool_pycharm(o):
    """
    Return the passed object unchanged.

    Used to force PyCharm not to perceive _SheetMeta as metaclass of Sheet.
    This allows PyCharm to assign correct types to Sheet subclasses.
    More about it in this issue: https://youtrack.jetbrains.com/issue/PY-46345

    :param o: any object
    :return: passed object
    """
    return o


_Row_co = TypeVar('_Row_co', covariant=True)


class Sheet(Generic[_Row_co], metaclass=_fool_pycharm(_SheetMeta)):
    spreadsheet: Spreadsheet
    index: Optional[int]
    title: Optional[str]
    transpose: bool
    row_class: type[Row]
    ignored_columns: set[str]

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
    def column(cls, index: int, /) -> str:
        if index <= 0:
            raise ValueError(f'column index must be positive, got {index}')

        if cls.transpose:
            return str(index)

        return _index2column(index)

    @classmethod
    def row(cls, index: int, /) -> str:
        if index <= 0:
            raise ValueError(f'row index must be positive, got {index}')

        if cls.transpose:
            return _index2column(index)

        return str(index)

    @classmethod
    def cell(cls, row: int, col: int, /) -> str:
        if cls.transpose:
            return f'{cls.row(row)}{cls.column(col)}'

        return f'{cls.column(col)}{cls.row(row)}'

    @classmethod
    def parse_values(cls, values: Sequence[Sequence[str]], /) -> Iterator[_Row_co]:
        columns = 'columns'
        if cls.transpose:
            values = tuple(zip(*values))
            columns = 'rows'

        # region Process column names
        names: dict[str, int] = {}
        for k, name in enumerate(values[0], 1):
            name = name.strip().lower()
            if len(name) == 0 or name in cls.ignored_columns:
                continue

            ins = names.setdefault(name, k)
            if ins != k:
                raise SheetParsingError(f'title repeated in {columns} {cls.column(k)} and {cls.column(ins)}')

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

        for i in range(2, len(values)):
            row = values[i - 1]
            args = {}
            for name, j in names.items():
                value = row[j - 1].strip()
                convert = row_class.titles2conversions_[name]
                try:
                    value = convert(value)
                except Exception as e:
                    # https://stackoverflow.com/a/24752607/14369408
                    raise SheetParsingError(f'{e.__class__.__name__} at cell {cls.cell(i, j)}: {e}') from e

                args[name] = value

            yield row_class.from_titles_(args)

    def __len__(self, /) -> int:
        return len(self._rows)

    @property
    def size(self, /) -> tuple[int, int]:
        return len(self.row_class.fields_), len(self._rows)

    def __contains__(self, item: _Row_co) -> bool:
        return item in self._rows

    def __iter__(self, /) -> Iterator[_Row_co]:
        return iter(self._rows)

    @overload
    def __getitem__(self, index: int, /) -> _Row_co: ...
    @overload
    def __getitem__(self, indexes: slice, /) -> tuple[_Row_co, ...]: ...
    @overload
    def __getitem__(self, cell: tuple[int, int], /) -> Any: ...
    @overload
    def __getitem__(self, subrow: tuple[slice, int], /) -> tuple[Any, ...]: ...
    @overload
    def __getitem__(self, subcol: tuple[int, slice], /) -> tuple[Any, ...]: ...
    @overload
    def __getitem__(self, cells: tuple[slice, slice], /) -> tuple[tuple[Any, ...], ...]: ...

    def __getitem__(self, item, /):
        if isinstance(item, tuple):
            col, row = item
            if isinstance(row, int):
                return self._rows[row][col]
            if isinstance(row, slice):
                return tuple(r[col] for r in self._rows[row])

            raise TypeError(f'sheet indices must be integers or slices, not {type(row)}')

        return self._rows[item]

    def __repr__(self, /) -> str:
        return str(self.__class__)

    def __init_subclass__(cls, /):
        if len(bases := cls.__bases__) != 1 or (len(bases) > 1 and bases[0] is not Sheet):
            raise TypeError(f'sheet must have only one base class and this class must be {Sheet.__name__!r}')

        fullname = f'{cls.__module__}.{cls.__qualname__}'

        # Check spreadsheet
        if hasattr(cls, 'spreadsheet'):
            if not isinstance(cls.spreadsheet, Spreadsheet):
                raise SheetDefinitionError(f'{fullname}.spreadsheet must be an instance of {Spreadsheet}, '
                                           f'got {type(cls.spreadsheet)}')
        else:
            raise SheetDefinitionError(f'sheet {fullname} does not have spreadsheet')

        # region Check index and title
        has_index = hasattr(cls, 'index')
        if has_index:
            if type(cls.index) is not int:
                raise SheetDefinitionError(f'{fullname}.index must be an integer, got {type(cls.index)}')
            elif cls.index < 0:
                raise SheetDefinitionError(f'{fullname}.index must be a non-negative integer, got {cls.index}')
        else:
            cls.index = None

        if hasattr(cls, 'title'):
            if type(cls.title) is not str:
                raise SheetDefinitionError(f'{fullname}.title must be a string, got {type(cls.title)}')
            elif len(cls.title) == 0:
                raise SheetDefinitionError(f'{fullname}.title must not be empty')
        elif has_index:
            cls.title = None
        else:
            cls.title = cls.__name__.replace('_', ' ').strip()
        # endregion

        # Get transpose value
        if hasattr(cls, 'transpose'):
            if not isinstance(cls.transpose, bool):
                raise SheetDefinitionError(f'sheet {fullname} has a non-bool value in transpose attribute')
        else:
            cls.transpose = False

        # region Extract and check row container class
        if hasattr(cls, '__orig_bases__'):
            cls.row_class = cls.__orig_bases__[0].__args__[0]
        elif not hasattr(cls, 'row_class'):
            raise SheetDefinitionError(f'sheet {fullname} does not have a row container class; '
                                       f'specify row container class when subclassing, i. e. '
                                       f'class YourSheet(Sheet[YourRowContainer])')

        if not isinstance(cls.row_class, type):
            raise SheetDefinitionError(f'sheet {fullname} has a non-class row container, '
                                       f'its type is {type(cls.row_class)}')

        if not issubclass(cls.row_class, Row):
            raise SheetDefinitionError(f'row container must be subclass of {Row.__name__}, '
                                       f'got {cls.row_class} for sheet {fullname}')
        # endregion

        # region Check ignored columns
        if hasattr(cls, 'ignored_columns'):
            if not isinstance(cls.ignored_columns, (set, frozenset)):
                raise SheetDefinitionError(f'sheet {fullname}.ignored_columns must be a set of strings, '
                                           f'got {type(cls.ignored_columns)}')

            for name in cls.ignored_columns:
                if not isinstance(name, str):
                    raise SheetDefinitionError(f'sheet {fullname}.ignored_columns must be a set of strings, '
                                               f'got value of type {type(name)}')

            cls.ignored_columns = {name.strip().lower() for name in cls.ignored_columns}
        else:
            cls.ignored_columns = set()
        # endregion
