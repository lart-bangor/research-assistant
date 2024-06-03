"""Data model for the AToL-C Task."""

from typing import List

from pydantic import BaseModel, Field, StringConstraints
from typing_extensions import Annotated

from ...datamodels import patterns as p
from ...datamodels.models import ResponseBase
from ...datamodels.types import UniqueList


class AtolcTaskLanguageRatings(BaseModel):
    """Single language rating for the AToL-C."""

    trial: int = Field(description="Trial number for this set of language ratings")

    language: Annotated[
        str, StringConstraints(strip_whitespace=True, pattern=p.SHORT_TEXT)
    ] = Field(description="ISO code of the language being rated")

    logic: Annotated[float, Field(ge=0, le=100)] = Field(
        description="Logical-Illogical rating"
    )

    elegance: Annotated[float, Field(ge=0, le=100)] = Field(
        description="Inelegant-Elegant rating"
    )

    fluency: Annotated[float, Field(ge=0, le=100)] = Field(
        description="Choppy-Fluent rating"
    )

    ambiguity: Annotated[float, Field(ge=0, le=100)] = Field(
        description="Unambiguous-Ambiguous rating"
    )

    appeal: Annotated[float, Field(ge=0, le=100)] = Field(
        description="Appealing-Abhorrent rating"
    )

    structure: Annotated[float, Field(ge=0, le=100)] = Field(
        description="Unstructured-Structured rating"
    )

    precision: Annotated[float, Field(ge=0, le=100)] = Field(
        description="Precise-Vague rating"
    )

    harshness: Annotated[float, Field(ge=0, le=100)] = Field(
        description="Harsh-Soft rating"
    )

    flow: Annotated[float, Field(ge=0, le=100)] = Field(
        description="Flowing-Abrupt rating"
    )

    beauty: Annotated[float, Field(ge=0, le=100)] = Field(
        description="Beautiful-Ugly rating"
    )

    sistem: Annotated[float, Field(ge=0, le=100)] = Field(
        description="Systematic-Unsystematic rating"
    )

    pleasure: Annotated[float, Field(ge=0, le=100)] = Field(
        description="Pleasant-Unpleasant rating"
    )

    smoothness: Annotated[float, Field(ge=0, le=100)] = Field(
        description="Smooth-Raspy rating"
    )

    grace: Annotated[float, Field(ge=0, le=100)] = Field(
        description="Clumsy-Graceful rating"
    )

    angularity: Annotated[float, Field(ge=0, le=100)] = Field(
        description="Angular-Round rating"
    )

    order: Annotated[UniqueList[str], Field(min_length=15, max_length=15)] = Field(
        description="Presentation order of the traits"
    )


class AtolcTaskResponse(ResponseBase):
    """AToL-C Task Response."""

    ratings: Annotated[List[AtolcTaskLanguageRatings], Field()] = Field(
        description="Ratings for each of the languages"
    )
