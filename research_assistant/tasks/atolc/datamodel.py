"""Data model for the AToL-C Task."""
from pydantic import BaseModel, constr, confloat, conlist, Field
from ...datamodels.models import ResponseBase
from ...datamodels import patterns as p


class AtolcTaskLanguageRatings(BaseModel):
    """Single language rating for the AToL-C."""

    language: constr(
        strip_whitespace=True,
        regex=p.SHORT_TEXT
        ) = Field(description="ISO code of the language being rated")

    logic: confloat(
        ge=0, le=100
        ) = Field(description="Logical-Illogical rating")

    elegance: confloat(
        ge=0, le=100
        ) = Field(description="Inelegant-Elegant rating")

    fluency: confloat(
        ge=0, le=100
        ) = Field(description="Choppy-Fluent rating")

    ambiguity: confloat(
        ge=0, le=100
        ) = Field(description="Unambiguous-Ambiguous rating")

    appeal: confloat(
        ge=0, le=100
        ) = Field(description="Appealing-Abhorrent rating")

    structure: confloat(
        ge=0, le=100
        ) = Field(description="Unstructured-Structured rating")

    precision: confloat(
        ge=0, le=100
        ) = Field(description="Precise-Vague rating")

    harshness: confloat(
        ge=0, le=100
        ) = Field(description="Harsh-Soft rating")

    flow: confloat(
        ge=0, le=100
        ) = Field(description="Flowing-Abrupt rating")

    beauty: confloat(
        ge=0, le=100
        ) = Field(description="Beautiful-Ugly rating")

    sistem: confloat(
        ge=0, le=100
        ) = Field(description="Systematic-Unsystematic rating")

    pleasure: confloat(
        ge=0, le=100
        ) = Field(description="Pleasant-Unpleasant rating")

    smoothness: confloat(
        ge=0, le=100
        ) = Field(description="Smooth-Raspy rating")

    grace: confloat(
        ge=0, le=100
        ) = Field(description="Clumsy-Graceful rating")

    angularity: confloat(
        ge=0, le=100
        ) = Field(description="Angular-Round rating")


class AtolcTaskResponse(ResponseBase):
    """AToL-C Task Response."""

    ratings: conlist(
        item_type=AtolcTaskLanguageRatings
    ) = Field(description="Ratings for each of the languages")
