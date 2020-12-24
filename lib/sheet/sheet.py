"""

TODO

- Использовать статические классы (синглтоны, обычные классы) для репрезентации листов.

- Иметь абстрактный  класс для листов с методами на извлечение строки, ряда, отдельной ячейки и т. п. При определении
подкласса делать проверки для требуемых полей. Для создания объекта будет передаваться матрица, которая при
необходимости будет транспонирована. Будут проверены названия колонок и их количество. После этого каждый ряд будет
прочитан, его значения будут сконвертированы в нужный тип и переданы в класс-ряд (именованный кортеж). При ошибке
конвертации выдавать ячейку, в которой произошла ошибка.

- В наследниках будут обязательны следующие поля: transpose, column_names. При необходимости можно будет определить
поле column_conversions, которое будет использоваться для конвертации значений в нужные типы. Если этого поля нет,
будут использоваться типы, определённые в именованном кортеже.

"""
from types import GenericAlias
from typing import Any, Callable, ClassVar, Generic, NamedTuple, Type, TypeVar

from common import isnamedtuplesubclass
from common.metaclasses import AllowInstantiation, EmptySlotsByDefaults, Singleton, combine


class SheetDefinitionError(Exception):
    pass


_Row_co = TypeVar('_Row_co', covariant=True)
_SheetMeta = combine(EmptySlotsByDefaults, AllowInstantiation)


class Sheet(Generic[_Row_co], metaclass=_SheetMeta, allow_instances=False):
    transpose: ClassVar[bool]
    column_names: ClassVar[tuple[str, ...]]
    column_conversions: ClassVar[tuple[Callable[[Any], Any], ...]]
    row_class: ClassVar[Type[NamedTuple]]

    __slots__ = '_rows'

    def __init__(self):
        pass

    def __init_subclass__(cls, *, special: bool = False, **kwargs):
        super().__init_subclass__(**kwargs)

        if special: return

        if hasattr(cls, 'transpose'):
            if not isinstance(cls.transpose, bool):
                raise SheetDefinitionError(f'sheet {cls.__qualname__} has non-bool value in transpose attribute')
        else:
            cls.transpose = False

        if not hasattr(cls, 'column_names'):
            raise SheetDefinitionError(f'sheet {cls.__qualname__} does not have column names')

        for index, name in enumerate(cls.column_names):
            if not isinstance(name, str):
                raise SheetDefinitionError(f'sheet {cls.__qualname__} has non-string value '
                                           f'in column names at index {index}')

        # Extract row container class
        if hasattr(cls, '__orig_bases__'):
            orig_bases: tuple[GenericAlias, ...] = cls.__orig_bases__
            for base in orig_bases:
                if issubclass(base.__origin__, Sheet):
                    cls.row_class = base.__args__[0]
                    break
        elif not hasattr(cls, 'row_class'):
            raise SheetDefinitionError(f'sheet {cls.__qualname__} does not have a row container class; '
                                       f'please, specify row container class when subclassing, i. e. '
                                       f'class YourSheet(Sheet[YourRowContainer])')

        if not isinstance(cls.row_class, type):
            raise SheetDefinitionError(f'sheet {cls.__qualname__} has non-class row container, '
                                       f'its type is {type(cls.row_class)}')

        # Define column conversions
        if not hasattr(cls, 'column_conversions'):
            if isnamedtuplesubclass(cls.row_class):
                cls.column_conversions = tuple(typ for typ in cls.row_class.__annotations__.values())
            else:
                raise SheetDefinitionError(f'sheet {cls.__qualname__} does not have column conversions; '
                                           f'please, specify them in column_conversions class attribute')

        for index, func in enumerate(cls.column_conversions):
            if not callable(func):
                raise SheetDefinitionError(f'sheet {cls.__qualname__} has non-callable object '
                                           f'in column conversions at index {index}')

        # Check column names and conversions length
        if len(cls.column_names) != len(cls.column_conversions):
            raise SheetDefinitionError(f'sheet {cls.__qualname__} has different number of column names and conversions')


class SingletonSheet(Sheet[_Row_co], metaclass=type(Sheet) @ Singleton, special=True, allow_instances=False):
    pass
