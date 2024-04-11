"""Data model for the LSBQe Task."""
from pydantic import BaseModel, Field, constr, conlist, conint, confloat
from datetime import date
from typing import Optional
from ...datamodels.models import ResponseBase
from ...datamodels import patterns as p


class LsbqeTaskResidency(BaseModel):
    """Temporally limited residency of an LSBQe respondent."""
    location: constr(
        strip_whitespace=True,
        regex=p.LOCATION_NAME
    ) = Field("Location (approx.) of residency.")

    start: date = Field("Start date of residency.")

    end: date = Field("End date of residency.")


class LsbqeTaskLsb(BaseModel):
    """Language and Social Background portion of the LSBQe."""
    sex: constr(
        strip_whitespace=True,
        to_lower=True,
        min_length=1,
        max_length=1,
        regex=r"^[mfo]$"
    ) = Field(description="Respondent's sex/gender.")

    sex_other: Optional[constr(
        strip_whitespace=True,
        regex=p.SHORT_TEXT
    )] = Field(description="Description of sex/gender if sex is 'other'.")

    occupation: constr(
        strip_whitespace=True,
        min_length=1,
        regex=p.SHORT_TEXT
    ) = Field(description="Respondent's occupation.")

    handedness: constr(
        strip_whitespace=True,
        to_lower=True,
        min_length=1,
        max_length=1,
        regex=r"^[rl]$"
    ) = Field(description="Respondent's handedness.")

    date_of_birth: date = Field(description="Respondent's date of birth.")

    hearing_impairment: bool = Field("Whether respondent has a hearing impairment or not.")

    hearing_aid: Optional[bool] = Field("Whether a hearing aid is used, if respondent has a hearing aid.")

    vision_impairment: bool = Field("Whether respondent has a vision impairment or not.")

    vision_aid: Optional[bool] = Field("Whether vision aids (glasses, contact lenses) are used, if respondent has a vision impairment.")

    vision_fully_corrected: Optional[bool] = Field("Whether vision aid fully corrects vision, if used.")

    place_of_birth: constr(
        strip_whitespace=True,
        regex=p.LOCATION_NAME
    ) = Field(description="Respondent's place of birth.")

    residencies: conlist(
        item_type=LsbqeTaskResidency,
        unique_items=True
    ) = Field("Respondent's past residencies over 6 month.")

    education_level: conint(
        ge=1, le=5
    ) = Field("Respondent's education level.")


class LsbqeLanguagesSpoken(BaseModel):
    """Languages spoken by an LSBQe respondent."""
    name: constr(
        strip_whitespace=True,
        regex=p.LANGUAGE_NAME
    ) = Field("Name of the language.")

    source_home: bool = Field("Whether the language was learned at home.")

    source_school: bool = Field("Whether the language was learned at school.")

    source_community: bool = Field("Whether the language was learned in the community.")

    source_other: Optional[constr(
        strip_whitespace=True,
        min_length=1,
        regex=p.SHORT_TEXT
    )] = Field("If applicable, other source(s) of language acquisition.")

    age: conint(
        ge=0, le=100
    ) = Field("Age at which the language was acquired.")

    breaks: conint(
        ge=0
    ) = "Total duration for which language was not used (?in days?)."

    proficiency_speaking: confloat(
        ge=0.0, le=100.0
    ) = Field("Proficiency in speaking language.")
    proficiency_understanding: confloat(
        ge=0.0, le=100.0
    ) = Field("Proficiency in understanding language.")
    proficiency_reading: Optional[confloat(
        ge=0.0, le=100.0
    )] = Field("Proficiency in reading language.")
    proficiency_writing: Optional[confloat(
        ge=0.0, le=100.0
    )] = Field("Proficiency in writing language.")

    usage_speaking: confloat(
        ge=0.0, le=0.0
    ) = Field(description="Proporition of use when speaking.")
    usage_listening: confloat(
        ge=0.0, le=0.0
    ) = Field(description="Proportion of use when listening.")
    usage_reading: Optional[confloat(
        ge=0.0, le=100.0
    )] = Field(description="Proportion of use when reading.")
    usage_writing: Optional[confloat(
        ge=0.0, le=100.0
    )] = Field(description="Proportion of use when writing.")


class LsbqeParentInformation(BaseModel):
    """Background information about a parent."""
    parent = constr(
        strip_whitespace=True,
        regex=r"^(?:mother|father)$"
    ) = Field("Is this for 'mother' or 'father'?")

    occupation: constr(
        strip_whitespace=True,
        min_length=1,
        regex=p.SHORT_TEXT
    ) = Field(description="Parent's occupation.")

    first_language: constr(
        strip_whitespace=True,
        min_length=1,
        regex=p.LANGUAGE_NAME
    ) = Field(description="Parent's first language.")

    second_language: Optional[constr(
        strip_whitespace=True,
        min_length=1,
        regex=p.LANGUAGE_NAME
    )] = Field(description="Parent's second language (if applicable).")

    other_languages: Optional[constr(
        strip_whitespace=True,
        min_length=1,
    )] = Field(description="List of parent's other languages (if applicable).")


class LsbqeTaskLdb(BaseModel):
    """Language and Dialect Background portion of the LSBQe."""

    languages_spoken: conlist(
        item_type=LsbqeLanguagesSpoken,
        min_items=1,
        unique_items=True
    ) = Field("Languages spoken by the respondent.")

    parents: conlist(
        item_type=LsbqeParentInformation,
        min_items=0,
        max_items=2,
        unique_items=True
    ) = Field("Information about respondent's parents.")


class LsbqeTaskClub(BaseModel):
    """Community Language Use Behaviour portion of the LSBQe."""

    ...


class LsbqeTaskResponse(ResponseBase):
    """LSBQe Task Response."""

    lsb: LsbqeTaskLsb

    ldb: LsbqeTaskLdb

    club: LsbqeTaskClub

    notes: Optional[str]
