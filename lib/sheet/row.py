import builtins
import sys
from _collections import _tuplegetter
from collections.abc import Callable
from typing import Any
from weakref import WeakSet

from common import repr_collection
from common.typing import Annotation
from .conversions import ConversionFunc

# TODO suggest to take type from .pyi stub file rather than in source

_row_attributes = frozenset((
    # in-source methods
    '__slots__', '__init__', '__new__', '__getnewargs__', '__init_subclass__',
    # values
    'fields_', 'column_names_', 'column_conversions_', 'subrows_', 'column_names_with_nested_',
    # methods
    '__repr__', 'replace_', 'as_dict_',
    # class methods
    'from_sheet_row_',
))
_rows = WeakSet()

_Methods = tuple[Callable, ...]


def _define_row_methods(row_: type['Row']) -> tuple[_Methods, _Methods, _Methods]:
    def __repr__(self, /) -> str:
        """Return a nicely formatted representation string"""
        f2v = ', '.join(f'{f}={v!r}' for f, v in zip(self.fields_, self))
        return f'{self.__class__.__name__}({f2v}))'

    def replace_(self, /, **kwargs) -> row_:
        result = self.__class__(*map(kwargs.pop, self.fields_, self))
        if kwargs:
            noun, rep = repr_collection(kwargs, 'name', 'names')
            raise ValueError(f'got unexpected field {noun} {rep}')

        return result

    replace_.__doc__ = f'Return a new {row_.__name__} instance replacing specified fields with new values'

    def as_dict_(self, /) -> dict[str, Any]:
        """Return a new dict which maps field names to their values"""
        return dict(zip(self.fields_, self))

    def from_sheet_row_(cls, column2value: dict[str, str], /) -> row_:
        keys = column2value.keys()
        all_cols = set(cls.column_names_with_nested_)
        if keys < all_cols:
            noun, rep = repr_collection(all_cols - keys, 'name', 'names')
            raise ValueError(f'missing necessary column {noun} {rep}')
        elif keys > all_cols:
            noun, rep = repr_collection(keys - all_cols, 'name', 'names')
            raise ValueError(f'unexpected column {noun} {rep}')

        args = [convert(column2value.pop(name)) for name, convert in
                zip(cls.column_names_, cls.column_conversions_)]

        for _, subrow in cls.subrows_:
            c2v = {name: column2value.pop(name) for name in subrow.column_names_with_nested_}
            args.append(subrow.from_sheet_row_(c2v))

        return cls(*args)

    from_sheet_row_.__doc__ = f'''
        Create a new {row_.__name__} instance from a dictionary with column names as keys 
        and raw content as values. 
        Dictionary keys must be the same as {row_.__name__}.column_names_with_nested_
    '''

    return (__repr__, replace_, as_dict_), (from_sheet_row_,), ()


def row(
        typename: str,
        fields: dict[str, tuple[Annotation, str, ConversionFunc]],
        subrows: dict[str, type['Row']],
        module: str = __name__,
        qualname: str = None
) -> type:
    lf = len(fields)
    ls = len(subrows)
    if lf + ls == 0:
        raise ValueError(f'row must have at least one field or subrow')
    if lf == 0 and ls == 1:
        raise ValueError(f'row cannot consist only from one subrow')

    if common := fields.keys() & subrows.keys():
        noun, rep = repr_collection(common, 'name', 'names')
        raise ValueError(f'field {noun} {rep} is duplicated in subrows')

    subrows = {sys.intern(f): t for f, t in subrows.items()}
    field2annotation = {sys.intern(f): t[0] for f, t in fields.items()} | subrows
    col_names = tuple(sys.intern(t[1].lower()) for t in fields.values())
    col_conversions = tuple(t[2] for t in fields.values())

    if common := _row_attributes & field2annotation.keys():
        noun, rep = repr_collection(common, 'attribute', 'attributes')
        raise ValueError(f'fields and subrows must not overwrite special {noun} {rep}')

    # region Check column names for duplicates in subrows and collect all column names
    seen = {}
    col_names_nested = {f: typename for f in col_names}
    for field, sr in subrows.items():
        if sr in seen:
            raise ValueError(f'row cannot have 2 fields of the same subrow, '
                             f'got {sr.__qualname__} for fields {seen[sr]!r} and {field!r}')
        seen[sr] = field
        for name in sr.column_names_with_nested_:
            inserted = col_names_nested.setdefault(name, sr)
            if inserted is not sr:
                raise ValueError(f'{inserted} and {sr} have identical column name {name!r}')

    col_names_nested = col_names if ls == 0 else tuple(col_names_nested)
    # endregion

    typename = sys.intern(typename)
    args = ', '.join(field2annotation)
    globals_ = dict(
        # necessary
        __builtins__=dict(__build_class__=builtins.__build_class__),
        __name__=module,
        # builtins
        tuple=tuple,
        TypeError=TypeError,
    )  # TODO compare performance of kw dict and sys.intern dict
    locals_ = {}

    source = f'''
class {typename}(tuple):
    __slots__ = ()

    def __init__(self, /, {args}):
        """Create a new instance of {typename}"""

    def __new__(cls, /, {args}):
        """Create a new instance of {typename}"""
        return tuple.__new__(cls, ({args},))

    def __getnewargs__(self, /):
        """Return self as a plain tuple. Used by copy and pickle"""
        return tuple(self)

    def __init_subclass__(cls, /, **kwargs):
        """Raise TypeError to restrict subclassing"""
        raise TypeError(f"type {typename} is not an acceptable base type")
'''
    exec(source, globals_, locals_)
    row_: type[tuple] = locals_[typename]
    # Update qualname if any
    if qualname:
        row_.__qualname__ = qualname
    else:
        qualname = row_.__qualname__
    # Update method annotations
    row_.__init__.__annotations__ = field2annotation.copy()
    row_.__new__.__annotations__ = {**field2annotation, 'return': row_}
    row_.__getnewargs__.__annotations__ = {'return': tuple[tuple(field2annotation.values())]}

    # region Set attributes
    setattr(row_, 'fields_', tuple(field2annotation))
    setattr(row_, 'column_names_', col_names)
    setattr(row_, 'column_conversions_', col_conversions)
    setattr(row_, 'subrows_', tuple(subrows.items()))
    setattr(row_, 'column_names_with_nested_', col_names_nested)
    # endregion

    # region Add field getters
    for i, f in enumerate(field2annotation):
        doc = sys.intern(f'Alias for field number {i}')
        setattr(row_, f, _tuplegetter(i, doc))
    # endregion

    # region Add methods
    methods, clsm, staticm = _define_row_methods(row_)
    for m in methods:
        setattr(row_, m.__name__, m)
    for m in clsm:
        setattr(row_, m.__name__, classmethod(m))
    for m in staticm:
        setattr(row_, m.__name__, staticmethod(m))
    # endregion

    # region Update __module__ and __qualname__ of all callables
    for name in _row_attributes:
        attr = row_.__dict__[name]
        if isinstance(attr, (classmethod, staticmethod)):
            attr = attr.__func__

        if callable(attr):
            attr.__module__ = module
            attr.__qualname__ = f'{qualname}.{attr.__name__}'
    # endregion

    # Add row to WeakSet of all rows
    _rows.add(row_)
    return row_


class RowMeta(type):
    # Attribute names
    rewrite_allowed = frozenset((
        '__repr__',
    ))
    rewrite_forbidden = _row_attributes - rewrite_allowed
    ignored = frozenset((
        '__name__',
    ))

    def __new__(mcs, typename: str, bases: tuple, namespace: dict, **kwargs):
        if len(bases) != 1 or (len(bases) > 1 and bases[0] is not Row):
            raise TypeError(f'row must have only one base class and this class must be {Row.__name__}')

        fields: dict[str, Annotation] = namespace.pop('__annotations__', {})
        module = namespace.pop('__module__', __name__)
        qualname = namespace.pop('__qualname__', typename)
        for attr in mcs.ignored:
            namespace.pop(attr, None)

        final_fields = {}
        subrows = {}
        for field, annotation in fields.items():
            if field.startswith('_') or field.endswith('_'):
                raise ValueError(f'field name must not start and end with underscore, got {field!r}')
            name = field.replace('_', ' ')

            if isinstance(annotation, type) and issubclass(annotation, Row):
                if field in namespace:
                    raise ValueError(f'subrow field must not have value, got {namespace[field]!r} for subrow {field!r}')
                subrows[field] = annotation
                continue

            convert = annotation
            if field in namespace:
                value = namespace.pop(field)
                if type(value) is str:
                    name = value
                elif callable(value):
                    convert = value
                elif type(value) is tuple:
                    if len(value) != 2:
                        raise ValueError(f'length of field tuple must be 2, got {len(value)} for {field!r}')

                    name, convert = value
                    if type(name) is not str:
                        raise TypeError(f'1st value of field tuple must be string, got {type(name)} for {field!r}')
                    if not callable(convert):
                        raise ValueError(f'2nd value of field tuple must be callable, got {convert!r} for {field!r}')
                else:
                    raise TypeError(f'field value can be string, callable or tuple, '
                                    f'got {value!r} of type {type(value)} for {field!r}')
            elif not callable(convert):
                raise ValueError(f'field annotation must be callable if no value is assigned, got {convert!r}')

            final_fields[field] = annotation, name, convert

        row_ = row(typename, final_fields, subrows, module, qualname)

        for attr in namespace:
            if attr in mcs.rewrite_forbidden:
                raise ValueError(f'cannot overwrite special {Row.__name__} attribute {attr!r}')
            else:
                setattr(row_, attr, namespace[attr])

        return row_

    def __call__(cls, *args, **kwargs):
        raise TypeError(f'class {cls.__name__} cannot be instantiated')

    def __subclasscheck__(self, subclass: type) -> bool:
        return self is subclass or subclass in _rows

    def __instancecheck__(self, instance: object) -> bool:
        return instance.__class__ in _rows


Row = type.__new__(RowMeta, 'Row', (), {})
