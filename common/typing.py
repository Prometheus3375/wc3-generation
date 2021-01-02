import types
import typing

Types_GenericAlias = types.GenericAlias
Typing_GenericAlias = type(typing.Final[int])
SpecialForm = type(typing.Union)
GenericAlias = Types_GenericAlias, Typing_GenericAlias  # for isinstance() and issubclass()

Annotation = typing.Union[
    type,
    Types_GenericAlias,
    Typing_GenericAlias,
    SpecialForm,
    typing.TypeVar,
    typing.ForwardRef
    # may be incomplete
]


def check_type(typ: Annotation, msg: str, is_argument: bool = True) -> Annotation:
    """
    Check that the argument is an annotation, and return it.
    If is_argument is True, also checks whether the argument is a valid annotation argument
    """
    return typing._type_check(typ, msg, is_argument)


def repr_type(a: Annotation) -> str:
    """Return the repr() of an annotation"""
    return typing._type_repr(a)
