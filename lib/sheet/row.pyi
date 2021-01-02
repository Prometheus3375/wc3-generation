from typing import Any, Final, TypeVar

from common import frozendict
from .conversions import ConversionFunc

_T = TypeVar('_T')


class Row(tuple):
    fields_: Final[tuple[str, ...]]
    column_names_: Final[frozendict[str, str]]
    column_conversions_: Final[frozendict[str, ConversionFunc]]
    subrows_: Final[frozendict[str, 'Row']]
    column_names_with_nested_: Final[frozenset[str]]

    def __init__(self, /, *args: Any):
        """Create a new instance"""

    def __new__(cls, /, *args: Any) -> 'Row':
        """Create a new instance"""

    def __getnewargs__(self, /) -> tuple[Any, ...]:
        """Return self as a plain tuple. Used by copy and pickle"""

    def replace_(self, /, **kwargs: Any) -> 'Row':
        """Return a new instance replacing specified fields with new values"""

    def as_dict_(self, /) -> dict[str, Any]:
        """Return a new dict which maps field names to their values"""

    @classmethod
    def from_sheet_row_(cls, column2value: dict[str, str], /) -> 'Row':
        """
        Create a new instance from a dictionary with column names as keys
        and raw content as values.
        Dictionary keys must be the same as cls.column_names_with_nested_
        """
