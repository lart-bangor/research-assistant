"""Data model for the Consent Task."""
from pydantic import Field
from ...datamodels.models import ResponseBase


class ConsentTaskResponse(ResponseBase):
    """Consent Task Response."""

    informed_consent: bool = Field(
        description="Whether the participant has given informed consent."
    )

    eligibility_confirmed: bool = Field(
        description="Whether the participant has confirmed eligibility."
    )
