"""Data model for the Memory Task."""

from typing import List

from pydantic import BaseModel, Field
from typing_extensions import Annotated

from ...datamodels.models import ResponseBase


class MemoryTaskScore(BaseModel):
    """Single score from a round of Memory."""

    score: Annotated[int, Field(ge=0)] = Field(description="Score from the Memory Task")
    time: Annotated[int, Field(ge=0)] = Field(
        description="Time played to end of round in seconds"
    )


class MemoryTaskResponse(ResponseBase):
    """Memory Task Response."""

    scores: Annotated[List[MemoryTaskScore], Field()] = Field(
        description="Scores from each round of Memory played"
    )
