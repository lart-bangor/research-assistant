"""Base models for L'ART Research Assistant Response models."""

import locale
import platform
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from typing_extensions import Annotated

from . import patterns as p


class ResponseMetadata(BaseModel):
    """Response metadata."""

    # Task information
    task_localisation: Annotated[
        str, StringConstraints(strip_whitespace=True, pattern=p.TASK_LOCALISATION_LABEL)
    ] = Field(description="Task localisation label")
    task_version_no: Annotated[
        str, StringConstraints(strip_whitespace=True, pattern=p.SOFTWARE_VERSION_NUMBER)
    ] = Field(description="Task version number")
    # App information
    app_version_no: Annotated[
        str, StringConstraints(strip_whitespace=True, pattern=p.SOFTWARE_VERSION_NUMBER)
    ] = Field(description="App version number")
    app_system_platform: str = Field(
        default_factory=lambda: f"{platform.platform()}_{platform.machine()}",
        description="System platform on which the response was collected",
    )
    app_system_useragent: str = Field(
        description="System useragent string that was used to collect the response"
    )
    app_display_language: Annotated[
        str, StringConstraints(strip_whitespace=True, pattern=p.SOFTWARE_LOCALE_STRING)
    ] = Field(
        default_factory=lambda: locale.getdefaultlocale()[0],
        description="Display language of the app used to collect the response",
    )
    # Researcher and participant information
    researcher_id: Annotated[
        str, StringConstraints(strip_whitespace=True, pattern=p.SHORT_ID)
    ] = Field(description="Researcher ID")
    research_location: Annotated[
        str, StringConstraints(strip_whitespace=True, pattern=p.LOCATION_NAME)
    ] = Field(description="Research location name")
    participant_id: Annotated[
        str, StringConstraints(strip_whitespace=True, pattern=p.SHORT_ID)
    ] = Field(description="Participant ID")
    consent_obtained: bool = Field(description="Consent confirmation")
    # Date information
    date_created: datetime = Field(
        default_factory=lambda: datetime.now(),
        description="Date and time the response was created",
    )
    date_modified: datetime = Field(
        default_factory=lambda: datetime.now(),
        description="Date and time the response was last modified",
    )


class ResponseBase(BaseModel):
    """Base model for Response models."""

    model_config = ConfigDict(
        validate_default=True,
        extra="forbid",
        use_enum_values=True,
        validate_assignment=True,
    )

    meta: ResponseMetadata
    id: uuid.UUID = Field(default_factory=uuid.uuid1, description="Response ID")

    @classmethod
    def get_required_fields(cls) -> set[str]:
        """Get the model's required fields."""
        required_fields: set[str] = set()
        for name, field in cls.model_fields.items():
            if field.is_required():
                required_fields.add(name)
        return required_fields
