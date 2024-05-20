"""Base models for L'ART Research Assistant Response models."""
import locale
import platform
import uuid
from datetime import datetime

from pydantic import BaseModel, Field, constr

from . import patterns as p


class ResponseMetadata(BaseModel):
    """Response metadata."""

    # Task information
    task_localisation: constr(
        strip_whitespace=True, regex=p.TASK_LOCALISATION_LABEL
    ) = Field(description="Task localisation label")
    task_version_no: constr(
        strip_whitespace=True, regex=p.SOFTWARE_VERSION_NUMBER
    ) = Field(description="Task version number")
    # App information
    app_version_no: constr(
        strip_whitespace=True, regex=p.SOFTWARE_VERSION_NUMBER
    ) = Field(description="App version number")
    app_system_platform: str = Field(
        default_factory=lambda: f"{platform.platform()}_{platform.machine()}",
        description="System platform on which the response was collected",
    )
    app_system_useragent: str = Field(
        description="System useragent string that was used to collect the response"
    )
    app_display_language: constr(
        strip_whitespace=True, regex=p.SOFTWARE_LOCALE_STRING
    ) = Field(
        default_factory=lambda: locale.getdefaultlocale()[0],
        description="Display language of the app used to collect the response",
    )
    # Researcher and participant information
    researcher_id: constr(strip_whitespace=True, regex=p.SHORT_ID) = Field(
        description="Researcher ID"
    )
    research_location: constr(strip_whitespace=True, regex=p.LOCATION_NAME) = Field(
        description="Research location name"
    )
    participant_id: constr(strip_whitespace=True, regex=p.SHORT_ID) = Field(
        description="Participant ID"
    )
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

    class Config:
        """Base configuration for Response models."""

        validate_all = True
        extra = "forbid"
        use_enum_values = True
        validate_assignment = True

    meta: ResponseMetadata
    id: uuid.UUID = Field(default_factory=uuid.uuid1, description="Response ID")

    @classmethod
    def get_required_fields(cls) -> set[str]:
        """Get the model's required fields."""
        required_fields: set[str] = set()
        for name, field in cls.__fields__.items():
            if field.required:
                required_fields.add(name)
        return required_fields
