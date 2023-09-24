"""Data model for the AGT Task."""
from pydantic import BaseModel, Field, constr, confloat, conlist
from ...datamodels.models import ResponseBase
from ...datamodels import patterns as p


agt_trial_pattern = r"^(?:practice|f[1-4]|s[1-4]_maj|s[1-4]_rml)$"


class AgtTaskTraitRating(BaseModel):
    """Rating of a single AGT trait on a single AGT audio stimulus."""

    trait: constr(
        strip_whitespace=True,
        to_lower=True,
        regex=p.SHORT_TEXT
    ) = Field(description="Name of the trait being rated.")

    rating: confloat(
        ge=0, le=100
    ) = Field(description="Rating value for the trait.")


class AgtTaskTrialRatings(BaseModel):
    """Ratings for a single AGT audio stimulus."""

    trial: constr(
        strip_whitespace=True,
        to_lower=True,
        regex=agt_trial_pattern
    ) = Field(description="Name of the trial (audio stimulus) being rated.")

    ratings: conlist(
        item_type=AgtTaskTraitRating,
        unique_items=True
    ) = Field(description="Ratings for each of the traits.")


class AgtTaskResponse(ResponseBase):
    """AGT Task Response."""

    stimulus_ratings: conlist(
        item_type=AgtTaskTrialRatings,
        unique_items=True
    ) = Field(description="Ratings for a given audio stimulus.")
