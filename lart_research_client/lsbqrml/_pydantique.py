"""Data Structure for the Language and Social Background Questionnaire (RML)."""
from typing import Any, Optional
from datetime import date
from enum import Enum
from pydantic import BaseModel, PastDate, constr, conint, validator

VersionLabel = constr(
    strip_whitespace=True,
    regex=r"\w",
    min_length=13,
    max_length=17
)

LocationName = constr(
    strip_whitespace=True,
    regex=r"\A[A-Za-z0-9, \(\)]\Z",
    min_length=1,
    max_length=50
)

ShortId = constr(
    strip_whitespace=True,
    regex=r"\A[A-Za-z0-9]\Z",
    min_length=3,
    max_length=10
)

LanguageName = constr(
    strip_whitespace=True,
    to_lower=True,
    min_length=3,  # Are there any shorter than 3 (Ido)?
    max_length=50
)

ShortText = constr(
    strip_whitespace=True,
    min_length=1,
    max_length=255
)

IsoYearMonthDay = constr(
    strip_whitespace=True,
    regex=r"\A[0-9]{1,4}-(0?[1-9]|1[0-2])-(0?[1-9]|[12][0-9]|3[01])\Z"
)

IsoYearMonth = constr(
    strip_whitespace=True,
    regex=r"\A[0-9]{1,4}-(0?[1-9]|1[0-2])\Z"

)

Likert5 = conint(
    strict=True,
    ge=1,
    le=5
)


class Sex(str, Enum):
    """Three-valued (m/f/o) enum for sex variables."""
    Male = "m"
    Female = "f"
    Other = "o"


class AcquisitionSource(str, Enum):
    """Indicated the source of acquisition of a language."""
    Home = "h"
    School = "s"
    Community = "c"
    Other = "o"


class Handedness(str, Enum):
    """Indicates whether someone is left- or right-handed."""
    Left = "l"
    Right = "r"


class MetaDataModel(BaseModel):
    """Meta Data for the LSBQ-RML."""

    version: VersionLabel
    researcher_id: ShortId
    research_location: LocationName
    participant_id: ShortId
    consent: bool
    date: Optional[IsoYearMonthDay]

    @validator("date", pre=True, always=True)
    @classmethod
    def todays_date(cls, v: Optional[IsoYearMonthDay]) -> IsoYearMonthDay:
        """Sets the date to today if not supplied."""
        if v is None or v == "":
            return date.today().isoformat()
        return v


class LsbDataModel(BaseModel):
    """Language and Social Background Data for the LSBQ-RML."""

    sex: Sex
    sex_other: Optional[ShortText]
    occupation: ShortText
    handedness: Handedness
    date_of_birth: PastDate
    hearing_impairment: bool
    hearing_aid: Optional[bool]
    vision_impairment: bool
    vision_aid: Optional[bool]
    vision_corrected: Optional[bool]
    place_of_birth: LocationName
    residency_locations: Optional[LocationName]
    residency_start: Optional[list[IsoYearMonth]]
    residency_end: Optional[list[IsoYearMonth]]
    education_level: Likert5

    @validator("sex_other", pre=True, always=True)
    @classmethod
    def sex_other_required(cls, v: ShortText, values: dict[str, Any]) -> ShortText:
        """Checks that sex_other is not None if sex was Sex.Other."""
        if v in (None, "") and values["sex"] is Sex.Other:
            raise ValueError("sex_other must be specified")
        return v

    @validator("hearing_aid", pre=True, always=True)
    @classmethod
    def hearing_aid_required(
        cls, v: Optional[bool], values: dict[str, Any]
    ) -> Optional[bool]:
        """Checks that hearing_aid is specificied if hearing_impairment is True."""
        if values["hearing_impairment"] is True and v is None:
            raise ValueError("hearing_aid must be specified")
        return v

    @validator("vision_aid", pre=True, always=True)
    @classmethod
    def vision_aid_required(
        cls, v: Optional[bool], values: dict[str, Any]
    ) -> Optional[bool]:
        """Checks that vision_aid is specificied if vision_impairment is True."""
        if values["vision_impairment"] is True and v is None:
            raise ValueError("vision_aid must be specified")
        return v

    @validator("vision_corrected", pre=True, always=True)
    @classmethod
    def vision_corrected_required(
        cls, v: Optional[bool], values: dict[str, Any]
    ) -> Optional[bool]:
        """Checks that vision_corrected is specificied if vision_aid is True."""
        if "vision_aid" in values and values["vision_aid"] is True and v is None:
            raise ValueError("vision_aid must be specified")
        return v

    @validator("residency_end", always=True)
    @classmethod
    def residency_matches(
        cls, v: Optional[list[str]], values: dict[str, Any]
    ) -> Optional[list[str]]:
        """Checks that residency_locations, residency_start, and residency_end match."""
        if "residency_locations" in values and values["residency_locations"] is not None:
            if "residency_start" not in values or values["residency_start"] is None:
                raise ValueError(
                    "at least one residency_locations but no residency_start provided"
                    )
            if v is None:
                raise ValueError(
                    "at least one residency_locations but no residency_end provided"
                    )
            len1, len2, len3 = (
                len(v),
                len(values["residency_locations"]),
                len(values["residency_start"])
            )
            if len1 != len2 or len1 != len3:
                raise ValueError(
                    "The number of residency_locations do not match residency_end "
                    "and/or residency_start"
                )
        return v


class NotesModel(BaseModel):
    """Notes for an LSBQ-RML questionnaire entry."""

    participant_note: Optional[str]
    researcher_note: Optional[str]


class LsbqRmlModel(BaseModel):
    """Model for the LSBQ-RML questionnaire."""

    instance: Optional[int]
    meta: MetaDataModel
    lsb: LsbDataModel
    notes: NotesModel
