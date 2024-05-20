"""Types and type aliases for L'ART Research Assistant data models."""
from typing import Hashable, TypeAlias, TypeVar
from uuid import UUID

AnyUUID: TypeAlias = UUID | str | bytes | int | tuple[int, int, int, int, int, int]
KeyT = TypeVar("KeyT", bound=Hashable)

_T = TypeVar("_T")
_V = TypeVar("_V")
