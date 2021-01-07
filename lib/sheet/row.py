import builtins
from _collections import _tuplegetter
from collections.abc import Callable
from sys import intern, modules
from typing import Any, Union
from weakref import WeakSet

from common import frozendict, repr_collection
from common.typing import Annotation, eval_hint
from .conversions import ConversionFunc

# TODO suggest to take type from .pyi stub file rather than in source
# TODO add special attribute ignored_columns_

_row_attributes = frozenset((
    # in-source methods
    '__slots__', '__init__', '__new__', '__getnewargs__', '__init_subclass__',
    # values
    'fields_', 'titles_', 'subrows_', 'titles2conversions_',
    # methods
    '__repr__', 'replace_', 'as_dict_',
    # class methods
    'from_titles_',
))
_forbidden_field_names = frozenset(('self', 'cls'))
_rows = WeakSet()

_Methods = tuple[Callable, ...]


def _define_row_methods(row_: type['Row']) -> tuple[_Methods, _Methods, _Methods]:
    def __repr__(self, /) -> str:
        """Return a nicely formatted representation string"""
        f2v = ', '.join(f'{f}={v!r}' for f, v in zip(self.fields_, self))
        return f'{self.__class__.__name__}({f2v})'

    def replace_(self, /, **kwargs) -> row_:
        result = self.__class__(*map(kwargs.pop, self.fields_, self))
        if kwargs:
            noun, rep = repr_collection(kwargs, 'name', 'names')
            raise ValueError(f'unexpected field {noun} {rep}')

        return result

    replace_.__doc__ = f'Return a new {row_.__name__} instance replacing specified fields with new values'

    def as_dict_(self, /) -> dict[str, Any]:
        """Return a new dict which maps field names to their values"""
        return dict(zip(self.fields_, self))

    def from_titles_(cls, title2value: dict[str, Any], /) -> row_:
        args = [title2value.pop(name) for name in cls.titles_.values()]

        for subrow in cls.subrows_.values():
            c2v = {name: title2value.pop(name) for name in subrow.titles2conversions_}
            args.append(subrow.from_titles_(c2v))

        if title2value:
            noun, rep = repr_collection(title2value, 'title', 'titles')
            raise ValueError(f'unexpected {noun} {rep}')

        return cls(*args)

    from_titles_.__doc__ = f'''
        Create a new {row_.__name__} instance from a dictionary with column titles as keys. 
        Dictionary keys must be the same as {row_.__name__}.titles2conversions_.keys()
    '''

    return (__repr__, replace_, as_dict_), (from_titles_,), ()


def row(
        typename: str,
        fields_: dict[str, tuple[Annotation, str, ConversionFunc]],
        subrows: dict[str, type['Row']],
        module: str = __name__,
        qualname: str = None
) -> type:
    lf = len(fields_)
    ls = len(subrows)
    if lf + ls == 0:
        raise ValueError(f'row must have at least one field or subrow')
    if lf == 0 and ls == 1:
        raise ValueError(f'row cannot consist only from one subrow')

    if common := fields_.keys() & subrows.keys():
        noun, rep = repr_collection(common, 'name', 'names')
        raise ValueError(f'field {noun} {rep} is duplicated in subrows')

    fields_ = {intern(k): v for k, v in fields_.items()}

    subrows = {intern(k): v for k, v in subrows.items()}
    fields = {f: t[0] for f, t in fields_.items()} | subrows
    titles = {f: intern(t[1].strip().lower()) for f, t in fields_.items()}
    conversions = {tit: tup[2] for tit, tup in zip(titles.values(), fields_.values())}
    del fields_

    if common := _row_attributes & fields.keys():
        noun, rep = repr_collection(common, 'attribute', 'attributes')
        raise ValueError(f'fields must not overwrite special {noun} {rep}')

    if common := _forbidden_field_names & fields.keys():
        (word, name), rep = repr_collection(common, ('word', 'name'), ('words', 'names'))
        raise ValueError(f'special {word} {rep} cannot be used as field {name}')

    # region Check column names for duplicates in subrows and collect all column titles
    seen = {}
    all_titles = {tit: typename for tit in conversions.keys()}
    for field, sr in subrows.items():
        if sr in seen:
            raise ValueError(f'row cannot have 2 fields of the same subrow, '
                             f'got {sr.__qualname__} for fields {seen[sr]!r} and {field!r}')
        seen[sr] = field
        for name in sr.titles2conversions_:
            inserted = all_titles.setdefault(name, sr)
            if inserted is not sr:
                if isinstance(inserted, str):
                    if qualname:
                        inserted = qualname
                    inserted = f'<class \'{module}.{inserted}\'>'
                raise ValueError(f'{inserted} and {sr} have identical column title {name!r}')

    for sr in subrows.values():
        conversions |= sr.titles2conversions_
    # endregion

    typename = intern(typename)
    args = ', '.join(fields)
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

    def __init_subclass__(cls, /):
        """Raise TypeError to restrict subclassing"""
        raise TypeError(f"type {typename!r} is not an acceptable base type")
'''
    exec(source, globals_, locals_)
    row_: type[tuple] = locals_[typename]
    # Update qualname if any
    if qualname:
        row_.__qualname__ = qualname
    else:
        qualname = row_.__qualname__
    # Update annotations
    row_.__annotations__ = fields
    row_.__init__.__annotations__ = fields.copy()
    row_.__new__.__annotations__ = {**fields, 'return': row_}
    row_.__getnewargs__.__annotations__ = {'return': tuple[tuple(fields.values())]}

    # region Set attributes
    setattr(row_, 'fields_', tuple(fields))
    setattr(row_, 'titles_', frozendict(titles))
    setattr(row_, 'subrows_', frozendict(subrows))
    setattr(row_, 'titles2conversions_', frozendict(conversions))
    # endregion

    # region Add field getters
    for i, f in enumerate(fields):
        doc = intern(f'Alias for field number {i}')
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
    ignored_attributes = frozenset((
        '__name__', '__annotations__', '__module__', '__qualname__',
    ))
    # Annotations
    ignored_annotations = frozenset((
        '__prefix__', '__postfix__'
    ))

    def __new__(mcs, typename: str, bases: tuple, namespace: dict, /):
        if len(bases) != 1 or (len(bases) > 1 and bases[0] is not Row):
            raise TypeError(f'row must have only one base class and this class must be {Row.__name__}')

        fields: dict[str, Union[Annotation, str]] = namespace.get('__annotations__', {})
        module = namespace.get('__module__', __name__)
        module_globals = modules[module].__dict__
        qualname = namespace.get('__qualname__', typename)
        for ann in mcs.ignored_annotations:
            fields.pop(ann, None)

        prefix = namespace.get('__prefix__', '')
        postfix = namespace.get('__postfix__', '')

        final_fields = {}
        subrows = {}
        for field, annotation in fields.items():
            if field.startswith('_'):
                raise ValueError(f'field name must not start with underscore, got {field!r}')
            name = field.replace('_', ' ').strip()

            if isinstance(annotation, str):
                annotation = eval_hint(annotation, module_globals, namespace)

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
                        raise ValueError(f'2nd value of field tuple must be callable, '
                                         f'got {convert!r} of type {type(convert)} for {field!r}')
                else:
                    raise TypeError(f'field value can be string, callable or tuple, '
                                    f'got {value!r} of type {type(value)} for {field!r}')
            elif not callable(convert):
                raise ValueError(f'field annotation must be callable if no value is assigned, '
                                 f'got {convert!r} of type {type(convert)} for {field!r}')

            final_fields[field] = annotation, f'{prefix}{name}{postfix}', convert

        row_ = row(typename, final_fields, subrows, module, qualname)

        for attr in mcs.ignored_attributes:
            namespace.pop(attr, None)

        for attr in namespace:
            if attr in mcs.rewrite_forbidden:
                raise ValueError(f'cannot overwrite special {Row.__name__} attribute {attr!r}')
            else:
                setattr(row_, attr, namespace[attr])

        return row_

    def __call__(cls, /, *args, **kwargs):
        raise TypeError(f'class {cls.__name__} cannot be instantiated')

    def __subclasscheck__(self, subclass: type, /) -> bool:
        return self is subclass or subclass in _rows

    def __instancecheck__(self, instance: object, /) -> bool:
        return instance.__class__ in _rows


Row = type.__new__(RowMeta, 'Row', (), {})
