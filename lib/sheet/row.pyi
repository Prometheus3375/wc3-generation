from typing import Any, Final, TypeVar

from .conversions import ConversionFunc

_T = TypeVar('_T')


class Row(tuple):
    fields: Final[tuple[str, ...]]
    column_names: Final[tuple[str, ...]]
    column_conversions: Final[tuple[ConversionFunc, ...]]

    def __init__(self: _T, *args: Any): ...

    def __new__(cls: type[_T], *args: Any) -> _T: ...

    def replace(self: _T, /, **kwargs) -> _T: ...

    def as_dict(self: _T) -> dict[str, Any]: ...
