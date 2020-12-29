"""

TODO

Возможно сделать вложенные подряды
Переделать fields, names и conversions в names -> fields и names -> conversions
Чтобы проверять, что объект является Row, заносить их всех в WeakRefSet

"""

import builtins
import sys
import typing
from _collections import _tuplegetter
from collections import deque
from io import StringIO
from types import GenericAlias
from typing import Any, Callable, Final, TypeVar, final

from .conversions import ConversionFunc

_T = TypeVar('_T')


def _type_check(hint: _T, msg: str, is_argument: bool = True) -> _T:
    """
    Check that the argument is a type hint, and return it.
    If is_argument is True, also checks whether hint is a valid type hint argument
    """
    return typing._type_check(hint, msg, is_argument)


def _type_repr(hint: _T) -> str:
    """Return the repr() of an object, special-casing types"""
    return typing._type_repr(hint)


_row_attributes = frozenset((
    '__slots__', '__init__', '__new__', '__getnewargs__', '__init_subclass__',
    'fields', 'column_names', 'column_conversions', 'replace', 'as_dict'
))

_ignored_attributes = frozenset(('__module__', '__name__', '__annotations__'))


def row(typename: str,
        fields: dict[str, Any],
        col_names: tuple[str, ...],
        col_converts: tuple[ConversionFunc, ...],
        module: str = '__main__') -> type:
    if not (len(fields) == len(col_names) == len(col_converts)):
        raise ValueError(f'lengths of fields, column names and column conversions must be equal, '
                         f'got {len(fields)}, {len(col_names)}, {len(col_converts)} respectively')

    if len(fields) == 0:
        raise ValueError(f'row must have at least one column')

    if not _row_attributes.isdisjoint(fields):
        attrs = ', '.join(_row_attributes & fields.keys())
        raise AttributeError(f'fields must not overwrite special attributes {attrs}')

    fields = {sys.intern(f): _type_check(t, f'field {f} annotation must be a type')
              for f, t in fields.items()}
    typename = sys.intern(str(typename))

    args_ann = ', '.join(f'{f}: {_type_repr(t)}' for f, t in fields.items())
    args = ', '.join(fields)
    globals_ = dict(
        # necessary
        __builtins__={'__build_class__': builtins.__build_class__},
        __name__=module,
        # builtins
        tuple=tuple,
        str=str,
        map=map,
        dict=dict,
        zip=zip,
        ValueError=ValueError,
        TypeError=TypeError,
        # typing
        Any=Any,
        Callable=Callable,
        ConversionFunc=ConversionFunc,
        Final=Final,
        final=final,
        # variables
        _tuplegetter=_tuplegetter,
        col_names=col_names,
        col_converts=col_converts,
        field_names=tuple(fields),
    )
    locals_ = {}

    # region Add type hints to globals
    seen = set()
    type_hints = deque(set(fields.values()))
    while type_hints:
        t = type_hints.popleft()
        seen.add(t)

        if isinstance(t, GenericAlias):
            if t.__origin__ not in seen:
                type_hints.append(t.__origin__)
            for arg in t.__args__:
                if arg not in seen:
                    type_hints.append(arg)
        else:
            r = _type_repr(t)
            if r in globals_:
                gr = globals_[r]
                if not (gr is t or gr == t):
                    raise KeyError(f'type representation {r} is identical for {gr!r} and {t!r}')
            else:
                globals_[r] = t
    # endregion

    getters = StringIO()
    for i, f in enumerate(fields):
        doc = sys.intern(f'Alias for field number {i}')
        getters.write(f'    {f} = _tuplegetter({i}, \'{doc}\')\n')

    source = f'''
@final
class {typename}(tuple):
    __slots__ = ()

    fields: Final[tuple[str, ...]] = field_names
    column_names: Final[tuple[str, ...]] = col_names
    column_conversions: Final[tuple[ConversionFunc, ...]] = col_converts

    def __init__(self, {args_ann}):
        """Create a new instance of {typename}({args})"""

    def __new__(cls, {args_ann}):
        """Create a new instance of {typename}({args})"""
        return tuple.__new__(cls, ({args},))

    def replace(self, /, **kwargs) -> '{typename}':
        """Return a new {typename} object replacing specified fields with new values"""
        result = self.__class__(*map(kwargs.pop, self.fields, self))
        if kwargs:
            raise ValueError(f"got unexpected field names: {{', '.join(kwargs)}}")
        
        return result

    def as_dict(self) -> dict[str, Any]:
        """Return a new dict which maps field names to their values"""
        return dict(zip(self.fields, self))

    def __repr__(self):
        """Return a nicely formatted representation string"""
        return f"{typename}({{', '.join(f'{{k}}={{v!r}}' for k, v in zip(self.fields, self))}})"

    def __getnewargs__(self):
        """Return self as a plain tuple. Used by copy and pickle"""
        return tuple(self)

    def __init_subclass__(cls, **kwargs):
        """Raise TypeError to restrict subclassing"""
        raise TypeError(f"type {typename} is not an acceptable base type")

{getters.getvalue()}
'''
    exec(source, globals_, locals_)
    return locals_[typename]


class RowMeta(type):
    def __new__(mcs, typename: str, bases: tuple, namespace: dict, **kwargs):
        if len(bases) != 1 or (len(bases) > 1 and bases[0] is not Row):
            raise TypeError(f'rows must have only one base class and this class must be {Row.__name__}')

        fields: dict[str, Any] = namespace.get('__annotations__', {})
        module = namespace.get('__module__', '__main__')

        col_names = []
        col_converts = []
        for field, convert in fields.items():
            if field.startswith('_') or field.endswith('_'):
                raise ValueError(f'field names must not start or end with underscore, got {field}')
            name = field.replace('_', ' ')

            if field in namespace:
                value = namespace[field]
                if not isinstance(value, tuple):
                    raise TypeError(f'type of fields must be tuple, got {type(value)} for {field}')
                lv = len(value)
                if lv == 0 or lv > 2:
                    raise ValueError(f'length of a field tuple must be 1 or 2, got {len(value)} for {field}')

                if lv == 1:
                    v = value[0]
                    if type(v) is str:
                        name = v
                    elif callable(v):
                        convert = v
                    else:
                        raise TypeError(f'field tuple of length 1 must contain either string or callable, '
                                        f'got {type(v)} for {field}')
                else:
                    name, convert = value
                    if not (type(name) is str and callable(convert)):
                        raise TypeError(f'field tuple of length 2 must contain string and callable, '
                                        f'got {type(name)} and {type(convert)} respectively for {field}')

            col_names.append(name)
            col_converts.append(convert)

        row_ = row(typename, fields, tuple(col_names), tuple(col_converts), module)

        for attr in namespace:
            if attr in _row_attributes:
                raise AttributeError(f'cannot overwrite special {Row.__name__} attribute {attr}')
            elif not (attr in _ignored_attributes or attr in fields):
                setattr(row_, attr, namespace[attr])

        return row_

    def __call__(cls, *args, **kwargs):
        raise TypeError(f'class {cls.__class__.__qualname__} cannot be instantiated')


Row = type.__new__(RowMeta, 'Row', (), {})
