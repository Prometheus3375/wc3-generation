from typing import Any, Final, TypeVar

from common import frozendict
from .conversions import ConversionFunc

_T = TypeVar('_T')


class Row(tuple):
    fields_: Final[tuple[str, ...]]
    titles_: Final[frozendict[str, str]]
    subrows_: Final[frozendict[str, 'Row']]
    titles2conversions_: Final[frozendict[str, ConversionFunc]]

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
    def from_titles_(cls, title2value: dict[str, Any], /) -> 'Row':
        """
        Create a new instance from a dictionary with column titles as keys.
        Dictionary keys must be the same as cls.titles2conversions_.keys()
        """
