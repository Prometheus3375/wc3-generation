"""

TODO

Иметь абстрактный  класс для листов с методами на извлечение строки, ряда, отдельной ячейки и т. п. При определении
подкласса делать проверки для требуемых полей. Для создания объекта будет передаваться матрица, которая при
необходимости будет транспонирована. Будут проверены названия колонок и их количество. После этого каждый ряд будет
прочитан, его значения будут сконвертированы в нужный тип и переданы в класс-ряд (именованный кортеж). При ошибке
конвертации выдавать ячейку, в которой произошла ошибка.

"""
from typing import ClassVar, Generic, TypeVar, final

from gspread import Spreadsheet

from common.metaclasses import AllowInstantiation, EmptySlotsByDefaults, Singleton, combine
from .row import Row


@final
class SheetDefinitionError(Exception):
    __module__ = 'builtins'  # https://stackoverflow.com/a/19419825


_Row_co = TypeVar('_Row_co', covariant=True)
_SheetMeta = combine(EmptySlotsByDefaults, AllowInstantiation, Singleton)


class Sheet(Generic[_Row_co], metaclass=_SheetMeta, allow_instances=False):
    spreadsheet: ClassVar[Spreadsheet]
    index: ClassVar[int]
    title: ClassVar[str]
    transpose: ClassVar[bool]
    row_class: ClassVar[type[Row]]

    __slots__ = '_rows'

    def __init__(self, /):
        pass

    def __init_subclass__(cls, /):
        bases = cls.__bases__
        if len(bases) != 1 or (len(bases) > 1 and bases[0] is not Sheet):
            raise TypeError(f'sheet must have only one base class and this class must be {Sheet.__name__!r}')

        fullname = f'{cls.__module__}.{cls.__qualname__}'

        # region Check spreadsheet
        if hasattr(cls, 'spreadsheet'):
            if not isinstance(cls.spreadsheet, Spreadsheet):
                raise SheetDefinitionError(f'{fullname}.spreadsheet must be instance of {Spreadsheet}, '
                                           f'got {type(cls.spreadsheet)}')
        else:
            raise SheetDefinitionError(f'sheet {fullname} does not have spreadsheet')

        # Check index and title
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
