import typing
from collections.abc import Iterable
from types import GenericAlias as _GenericAlias
from typing import Final, ForwardRef, Protocol, TypeVar, Union

Types_GenericAlias = _GenericAlias
Typing_GenericAlias = type(Final[int])
SpecialForm = type(Union)
GenericAlias = Types_GenericAlias, Typing_GenericAlias  # for isinstance() and issubclass()
Real = Union[int, float]
real = int, float  # for isinstance() and issubclass()

Annotation = Union[
    type,
    Types_GenericAlias,
    Typing_GenericAlias,
    SpecialForm,
    TypeVar,
    ForwardRef,
    # may be incomplete
]

_K = TypeVar('_K')
_T = TypeVar('_T')
_V_co = TypeVar('_V_co', covariant=True)


def check_type(typ: Annotation, msg: str, is_argument: bool = True) -> Annotation:
    """
    Check that the argument is an annotation, and return it.
    If is_argument is True, also checks whether the argument is a valid annotation argument
    """
    return typing._type_check(typ, msg, is_argument)


def repr_type(a: Annotation) -> str:
    """Return the repr() of an annotation"""
    return typing._type_repr(a)


def eval_type(obj: Annotation, globals_: dict, locals_: dict, recursive_guard: frozenset = frozenset()) -> Annotation:
    """
    Evaluate all forward references in the given type t.
    For use of globals_ and locals_ see the docstring for get_type_hints().
    recursive_guard is used to prevent infinite recursion with recursive ForwardRef.
    """
    return typing._eval_type(obj, globals_, locals_, recursive_guard)


def eval_hint(hint: str, /, globals_: dict = None, locals_: dict = None):
    return ForwardRef(hint, False)._evaluate(globals_, locals_, frozenset())


class SupportsKeysAndGetItem(Protocol[_K, _V_co]):
    def keys(self, /) -> Iterable[_K]: ...
    def __getitem__(self, item: _K, /) -> _V_co: ...


class SupportsLessThan(Protocol[_T]):
    def __lt__(self: _T, other: _T, /) -> bool: ...
