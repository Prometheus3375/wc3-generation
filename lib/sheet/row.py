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


# attributes prohibited to set in Row subclass
_prohibited = frozenset((
    '__slots__', '__init__', '__new__', '__getnewargs__', '__init_subclass__',
    'fields', 'column_names', 'column_conversions', 'replace', 'as_dict'
))

_special = frozenset(('__module__', '__name__', '__annotations__'))


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

    # Add type hints to globals
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
        result = self.__class__(*map(kwargs.pop, field_names, self))
        if kwargs:
            raise ValueError(f"got unexpected field names: {{', '.join(kwargs)}}")
        
        return result

    def as_dict(self) -> dict[str, Any]:
        """Return a new dict which maps field names to their values"""
        return dict(zip(field_names, self))

    def __repr__(self):
        """Return a nicely formatted representation string"""
        return f"{typename}({{', '.join(f'{{k}}={{v!r}}' for k, v in zip(field_names, self))}})"

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

        fields = namespace.get('__annotations__', {})
        module = namespace.get('__module__', '__main__')

        col_names = []
        col_converts = []
        for name in fields:
            if name in namespace:
                value = namespace[name]
                if not isinstance(value, tuple):
                    raise ValueError(f'type of fields must be tuple, got {type(name)} for {name}')
                if len(value) == 0 or len(value) > 2:
                    raise ValueError(f'length of a field tuple must be 1 or 2, got {len(value)} for {name}')

                # TODO проверять, что имя str, а конвертация callable
                # Разрешить вариант, где имя берётся из аннотации, а конвертация из тупла
                # Возможно сделать вложенные подряды
                # Переделать fields, names и conversions в names -> fields и names -> conversions
                # если имя берётся из аннотации, то _ конвертируются в пробелы; запретить _ в начале и конце имён
                # чтобы проверять, что объект является Row, заносить их всех в WeakRefSet

                name = value[0]
                convert = value[1] if len(value) == 2 else fields[name]
            else:
                convert = fields[name]

            col_names.append(name)
            col_converts.append(convert)

        row_ = row(typename, fields, tuple(col_names), tuple(col_converts), module)

        for attr in namespace:
            if attr in _prohibited:
                raise AttributeError(f'cannot overwrite special {Row.__name__} attribute {attr}')
            elif not (attr in _special or attr in fields):
                setattr(row_, attr, namespace[attr])

        return row_


Row = type.__new__(RowMeta, 'Row', (), {})
