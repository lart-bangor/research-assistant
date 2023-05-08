"""Data models and utilities for the L'ART Research Assistant."""

from pydantic import BaseModel, Field, constr, schema_json_of
import uuid


TASK_VERSION_TAG = r"[A-Z][a-z]{2}[A-Z][a-z]{2}_[A-Z][a-z]{2}_[A-Z]{2}"
APP_VERSION_NUMBER = r"(?:\d+.)*\d+\w?\w?\d*" # 3, 0.4, 1.0a, 24.2.4rc45 etc.


class ResponseMetadata(BaseModel):
    """Response metadata."""

    # Task information
    task_version_tag: constr(
        strip_whitespace=True,
        regex=TASK_VERSION_TAG
        ) = Field(description="The task's version identifier tag.")
    task_version_no: constr(
        strip_whitespace=True,
        regex=APP_VERSION_NUMBER
        ) = Field(description="The task's version number.")
    # App information
    app_version_no: constr(
        strip_whitespace=True,
        regex=APP_VERSION_NUMBER
        ) = Field(description="The app's version number.")
    app_system_platform: str = Field(
        description="The system platform on which the response was collected."
        )
    app_system_webviewer: str = Field(
        description="The system webview component that was used to collect the response."
        )
    app_display_language: str = Field(
        description="The display language of the app used to collect the response."
        )
    # Researcher and participant information
    researcher_id: str
    research_location: str
    participant_id: str
    consent_obtained: str
    # Date information
    date_created: str
    date_modified: str


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


print(schema_json_of(ResponseMetadata, title="Test Schema", indent=2))
