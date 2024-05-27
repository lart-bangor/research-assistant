"""Data model for the Consent Task."""

from pydantic import Field, StringConstraints
from typing_extensions import Annotated

from ...datamodels import patterns as p
from ...datamodels.models import ResponseBase


class ConsentTaskResponse(ResponseBase):
    """Consent Task Response."""

    consent_task_group: Annotated[
        str, StringConstraints(strip_whitespace=True, pattern=p.SHORT_TEXT)
    ] = Field(description="The task group for which consent was obtained.")

    informed_consent: bool = Field(
        description="Whether the participant has given informed consent."
    )

    eligibility_confirmed: bool = Field(
        description="Whether the participant has confirmed eligibility."
    )
