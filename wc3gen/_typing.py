from types import GenericAlias as _GenericAlias
from typing import Final, ForwardRef, TypeVar, Union

Types_GenericAlias = _GenericAlias
Typing_GenericAlias = type(Final[int])
SpecialForm = type(Union)
GenericAlias = Types_GenericAlias, Typing_GenericAlias  # for isinstance() and issubclass()

Annotation = Union[
    type,
    Types_GenericAlias,
    Typing_GenericAlias,
    SpecialForm,
    TypeVar,
    ForwardRef,
    # may be incomplete
]


def eval_hint(hint: str, /, globals_: dict = None, locals_: dict = None):
    return ForwardRef(hint, False)._evaluate(globals_, locals_, recursive_guard=frozenset())
