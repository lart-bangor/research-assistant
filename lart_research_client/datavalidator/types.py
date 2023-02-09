"""Type definitions for the datavalidator package."""
from typing import Any, Iterable, Union, TypeVar

XT = TypeVar("XT")
YT = TypeVar("YT")

RangeT = Union[
    tuple[int, int], tuple[float, float],
    list[int], list[float]
]
"""Type for inclusive numeric ranges (int or float).

Examples:
    - (1, 10) validates integers and floats 1 through 10 inclusive.
    - (1.0, 10.0) same  as (1, 10).
    - (0.5, 9.5) validates integers 1 through 10 inclusive, but floats
      only from 0.50 to 9.50 inclusive.
    - [1, 10] same as (1, 10).
    - [0.5, 9.5] same as (0.5, 9.5).
"""

SetT = Iterable[Any]
"""Type for checking whether whether a value is contained in a set.

Examples:
    - (1, 2, 3) checks whether a given value is equal to the integer 1, 2, or 3.
    - (True, False) checks whether a given value evaluates to True or False.
    - {"A", "b", 3} checks whether a given value equals "A", "b", or the int 3.
"""

PolarT = Union[
    tuple[Iterable[Any], Iterable[Any]],
    list[Iterable[Any]]
]
"""Type for checking whether value falls within a set of polar items.

Examples:
    - ({"yes", "on", "true"}, {"no", "off", "false"}) checks whether a given
      value is in the set {"yes", "on", "true"} or the set {"no", "off", "false"},
      and depending on the function might return True for the former set and
      False for the latter.
"""

PatternT = str
r"""Type for regular expression patterns for string matching.

Note: In use, a PatternT string will always be annotated with a preceding r"\A"
      and a succeeding r"\Z" to match the start and end of a string exhaustively.

Examples:
    - r"\w*" will match anything matched by r"\A\w*\Z".
"""

EnumT = dict[Any, Any]
"""Type for enumerable checking and valuation.

Note: The dictionary keys and values can be any type. If a value repeats for
      more than one individual key it will be treated as an alias.

Examples:
    - {"A": 1, "B": 2} will match inputs "A", 1, "B", and 2, and cast to either
      1 or 2.
"""
