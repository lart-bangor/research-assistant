"""Types and type aliases for L'ART Research Assistant data models."""

from typing import Annotated, Collection, Hashable, TypeAlias, TypeVar
from uuid import UUID

from pydantic import AfterValidator, Field
from pydantic_core import PydanticCustomError

AnyUUID: TypeAlias = UUID | str | bytes | int | tuple[int, int, int, int, int, int]
KeyT = TypeVar("KeyT", bound=Hashable)

_T = TypeVar("_T")
_V = TypeVar("_V")


def _validate_unique_collection(c: Collection[KeyT]) -> Collection[KeyT]:
    if len(c) != len(set(c)):
        raise PydanticCustomError("unique_collection", "Collection must be unique")
    return c


UniqueCollection: TypeAlias = Annotated[
    Collection[KeyT],
    AfterValidator(_validate_unique_collection),
    Field(json_schema_extra={"uniqueItems": True}),
]

UniqueList: TypeAlias = Annotated[
    list[KeyT],
    AfterValidator(_validate_unique_collection),
    Field(json_schema_extra={"uniqueItems": True}),
]
