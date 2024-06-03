"""Data model for the AGT Task."""

from typing import Annotated, Any

from pydantic import BaseModel, Field, StringConstraints

from ...datamodels import patterns as p
from ...datamodels.models import ResponseBase
from ...datamodels.types import UniqueList

agt_trial_pattern = r"^(?:practice|f[1-4]|s[1-4]_maj|s[1-4]_rml)$"


class AgtTaskTraitRating(BaseModel):
    """Rating of a single AGT trait on a single AGT audio stimulus."""

    trait: Annotated[
        str,
        StringConstraints(strip_whitespace=True, to_lower=True, pattern=p.SHORT_TEXT),
    ] = Field(description="Name of the trait being rated.")

    rating: Annotated[float, Field(ge=0, le=100)] = Field(
        description="Rating value for the trait."
    )

    def __hash__(self) -> int:
        """Return a hash computed from the *trait* and *rating*."""
        return hash((self.trait, self.rating))

    def __eq__(self, other: Any) -> bool:
        """Compare two instances of `AgtTaskTraitRating` for equality.

        They are considerd equal if both the *trait* and the *rating* properties
        compare as equal.
        """
        if isinstance(other, self.__class__):
            return self.trait == other.trait and self.rating == other.rating
        return NotImplemented


class AgtTaskTrialRatings(BaseModel):
    """Ratings for a single AGT audio stimulus."""

    trial: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True, to_lower=True, pattern=agt_trial_pattern
        ),
    ] = Field(description="Name of the trial (audio stimulus) being rated.")

    ratings: UniqueList[AgtTaskTraitRating] = Field(
        description="Ratings for each of the traits."
    )

    def __hash__(self) -> int:
        """Return a hash computed from the *trait* and *rating*."""
        return hash((self.trial, self.ratings))

    def __eq__(self, other: Any) -> bool:
        """Compare two instances of `AgtTaskTrialRatings` for equality.

        They are considerd equal if both the *trial* and the *ratings*
        properties compare as equal.
        """
        if isinstance(other, self.__class__):
            return self.trial == other.trial and self.ratings == other.ratings
        return NotImplemented


class AgtTaskResponse(ResponseBase):
    """AGT Task Response."""

    stimulus_ratings: UniqueList[AgtTaskTrialRatings] = Field(
        description="Ratings for a given audio stimulus."
    )
