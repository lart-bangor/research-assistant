"""Data model for the Memory Task."""
from pydantic import BaseModel, conint, conlist, Field
from ..datamodels.models import ResponseBase


class MemoryTaskScore(BaseModel):
    """Single score from a round of Memory."""

    score: conint(
        ge=0
        ) = Field(description="Score from the Memory Task")
    time: conint(
        ge=0
        ) = Field(description="Time played to end of round in seconds")


class MemoryTaskResponse(ResponseBase):
    """Memory Task Response."""

    scores: conlist(
        item_type=MemoryTaskScore
        ) = Field(description="Scores from each round of Memory played")
