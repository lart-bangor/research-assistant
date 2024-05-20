"""Data model for the LSBQe Task."""
from datetime import date
from typing import Optional

from pydantic import (BaseModel, Field, PastDate, confloat, conint, conlist,
                      constr)

from ...datamodels import patterns as p
from ...datamodels.models import ResponseBase


class LsbqeTaskResidency(BaseModel):
    """Temporally limited residency of an LSBQe respondent."""

    location: constr(strip_whitespace=True, regex=p.LOCATION_NAME) = Field(
        "Location (approx.) of residency."
    )

    start: PastDate = Field("Start date of residency.")

    end: date = Field("End date of residency.")


class LsbqeTaskLsb(BaseModel):
    """Language and Social Background portion of the LSBQe."""

    sex: constr(
        strip_whitespace=True,
        to_lower=True,
        min_length=1,
        max_length=1,
        regex=r"^[mfo]$",
    ) = Field(description="Respondent's sex/gender.")

    sex_other: Optional[constr(strip_whitespace=True, regex=p.SHORT_TEXT)] = Field(
        description="Description of sex/gender if sex is 'other'."
    )

    occupation: constr(strip_whitespace=True, min_length=1, regex=p.SHORT_TEXT) = Field(
        description="Respondent's occupation."
    )

    handedness: constr(
        strip_whitespace=True,
        to_lower=True,
        min_length=1,
        max_length=1,
        regex=r"^[rl]$",
    ) = Field(description="Respondent's handedness.")

    date_of_birth: PastDate = Field(description="Respondent's date of birth.")

    hearing_impairment: bool = Field(
        description="Whether respondent has a hearing impairment or not."
    )

    hearing_aid: Optional[bool] = Field(
        description="Whether a hearing aid is used, if respondent has a hearing aid."
    )

    vision_impairment: bool = Field(
        description="Whether respondent has a vision impairment or not."
    )

    vision_aid: Optional[bool] = Field(
        description="Whether vision aids (glasses, contact lenses) are used, if respondent has a vision impairment."
    )

    vision_fully_corrected: Optional[bool] = Field(
        description="Whether vision aid fully corrects vision, if used."
    )

    place_of_birth: constr(strip_whitespace=True, regex=p.LOCATION_NAME) = Field(
        description="Respondent's place of birth."
    )

    residencies: conlist(item_type=LsbqeTaskResidency, unique_items=True) = Field(
        description="Respondent's past residencies over 6 month."
    )

    education_level: conint(ge=1, le=5) = Field(
        description="Respondent's education level."
    )


class LsbqeLanguageSpoken(BaseModel):
    """Language spoken by an LSBQe respondent."""

    name: constr(strip_whitespace=True, regex=p.LANGUAGE_NAME) = Field(
        description="Name of the language."
    )

    source_home: bool = Field(description="Whether the language was learned at home.")

    source_school: bool = Field(
        description="Whether the language was learned at school."
    )

    source_community: bool = Field(
        description="Whether the language was learned in the community."
    )

    source_other: Optional[
        constr(strip_whitespace=True, min_length=1, regex=p.SHORT_TEXT)
    ] = Field(description="If applicable, other source(s) of language acquisition.")

    age: conint(ge=0, le=100) = Field(
        description="Age at which the language was acquired."
    )

    breaks: conint(ge=0) = Field(
        description="Total duration for which language was not used in months."
    )

    proficiency_speaking: confloat(ge=0.0, le=100.0) = Field(
        description="Proficiency in speaking language."
    )
    proficiency_understanding: confloat(ge=0.0, le=100.0) = Field(
        description="Proficiency in understanding language."
    )
    proficiency_reading: Optional[confloat(ge=0.0, le=100.0)] = Field(
        description="Proficiency in reading language."
    )
    proficiency_writing: Optional[confloat(ge=0.0, le=100.0)] = Field(
        description="Proficiency in writing language."
    )

    usage_speaking: confloat(ge=0.0, le=100.0) = Field(
        description="Proporition of use when speaking."
    )
    usage_listening: confloat(ge=0.0, le=100.0) = Field(
        description="Proportion of use when listening."
    )
    usage_reading: Optional[confloat(ge=0.0, le=100.0)] = Field(
        description="Proportion of use when reading."
    )
    usage_writing: Optional[confloat(ge=0.0, le=100.0)] = Field(
        description="Proportion of use when writing."
    )


class LsbqeParentInformation(BaseModel):
    """Background information about a parent."""

    parent: constr(strip_whitespace=True, regex=r"^(?:mother|father)$") = Field(
        description="Is this for 'mother' or 'father'?"
    )

    occupation: constr(strip_whitespace=True, min_length=1, regex=p.SHORT_TEXT) = Field(
        description="Parent's occupation."
    )

    first_language: constr(
        strip_whitespace=True, min_length=1, regex=p.LANGUAGE_NAME
    ) = Field(description="Parent's first language.")

    second_language: Optional[
        constr(strip_whitespace=True, min_length=1, regex=p.LANGUAGE_NAME)
    ] = Field(description="Parent's second language (if applicable).")

    other_languages: Optional[
        constr(
            strip_whitespace=True,
            min_length=1,
        )
    ] = Field(description="List of parent's other languages (if applicable).")


class LsbqeTaskLdb(BaseModel):
    """Language and Dialect Background portion of the LSBQe."""

    languages_spoken: conlist(
        item_type=LsbqeLanguageSpoken, min_items=1, unique_items=True
    ) = Field(description="Languages spoken by the respondent.")

    parents: conlist(
        item_type=LsbqeParentInformation, min_items=0, max_items=2, unique_items=True
    ) = Field(description="Information about respondent's parents.")


class LsbqeTaskClubLifeStages(BaseModel):
    """Language use during different (early) life stages."""

    infancy_age: confloat(ge=0.0, le=100.0) = Field(
        description="Proportion of language use in infancy age."
    )

    nursery_age: confloat(ge=0.0, le=100.0) = Field(
        description="Proportion of language use in nursery age."
    )

    primary_age: confloat(ge=0.0, le=100.0) = Field(
        description="Proportion of language use in primary school age."
    )

    secondary_age: confloat(ge=0.0, le=100.0) = Field(
        description="Proportion of language use in secondary school age."
    )


class LsbqeTaskClubPeopleCurrent(BaseModel):
    """Language use with different groups of people, currently."""

    parents: Optional[confloat(ge=0.0, le=100.0)] = Field(
        description="Proportion of language use with parents."
    )

    children: Optional[confloat(ge=0.0, le=100.0)] = Field(
        description="Proportion of language use with children."
    )

    siblings: Optional[confloat(ge=0.0, le=100.0)] = Field(
        description="Proportion of language use with siblings."
    )

    grandparents: Optional[confloat(ge=0.0, le=100.0)] = Field(
        description="Proportion of language use with grandparents."
    )

    other_relatives: Optional[confloat(ge=0.0, le=100.0)] = Field(
        description="Proportion of language use with other relatives."
    )

    partner: Optional[confloat(ge=0.0, le=100.0)] = Field(
        description="Proportion of language use with partner."
    )

    friends: Optional[confloat(ge=0.0, le=100.0)] = Field(
        description="Proportion of language use with friends."
    )

    flatmates: Optional[confloat(ge=0.0, le=100.0)] = Field(
        description="Proportion of language use with flatmates/roommates."
    )

    neighbours: Optional[confloat(ge=0.0, le=100.0)] = Field(
        description="Proportion of language use with neighbours."
    )


class LsbqeTaskClubPeopleChildhood(BaseModel):
    """Language use with different groups of people during childhood."""

    parents: Optional[confloat(ge=0.0, le=100.0)] = Field(
        description="Proportion of language use with parents during childhood."
    )

    siblings: Optional[confloat(ge=0.0, le=100.0)] = Field(
        description="Proportion of language use with siblings during childhood."
    )

    grandparents: Optional[confloat(ge=0.0, le=100.0)] = Field(
        description="Proportion of language use with grandparents during childhood."
    )

    other_relatives: Optional[confloat(ge=0.0, le=100.0)] = Field(
        description="Proportion of language use with other relatives during childhood."
    )

    friends: Optional[confloat(ge=0.0, le=100.0)] = Field(
        description="Proportion of language use with friends during childhood."
    )

    neighbours: Optional[confloat(ge=0.0, le=100.0)] = Field(
        description="Proportion of language use with neighbours during childhood."
    )


class LsbqeTaskClubSituations(BaseModel):
    """Language use in different situations/settings."""

    home: Optional[confloat(ge=0.0, le=100.0)] = Field(
        description="Proportion of language use at home."
    )

    school: Optional[confloat(ge=0.0, le=100.0)] = Field(
        description="Proportion of language use in school."
    )

    work: Optional[confloat(ge=0.0, le=100.0)] = Field(
        description="Proportion of language use at work."
    )

    socialising: Optional[confloat(ge=0.0, le=100.0)] = Field(
        description="Proportion of language use when socialising."
    )

    religion: Optional[confloat(ge=0.0, le=100.0)] = Field(
        description="Proportion of language use for religious activities."
    )

    leisure: Optional[confloat(ge=0.0, le=100.0)] = Field(
        description="Proportion of language use for leisure activities."
    )

    commercial: Optional[confloat(ge=0.0, le=100.0)] = Field(
        description="Proportion of language use for commercial activities."
    )

    public: Optional[confloat(ge=0.0, le=100.0)] = Field(
        description="Proportion of language use for public affairs."
    )


class LsbqeTaskClubActivities(BaseModel):
    """Language use for different activities."""

    reading: Optional[confloat(ge=0.0, le=100.0)] = Field(
        description="Proportion of language use for reading."
    )

    emailing: Optional[confloat(ge=0.0, le=100.0)] = Field(
        description="Proportion of language use for emailing."
    )

    texting: Optional[confloat(ge=0.0, le=100.0)] = Field(
        description="Proportion of language use for texting (SMS, WhatsApp, ...)."
    )

    social_media: Optional[confloat(ge=0.0, le=100.0)] = Field(
        description="Proportion of language use with social media."
    )

    notes: Optional[confloat(ge=0.0, le=100.0)] = Field(
        description="Proportion of language use for notes/memos."
    )

    traditional_media: Optional[confloat(ge=0.0, le=100.0)] = Field(
        description="Proportion of language use with traditional media."
    )

    internet: Optional[confloat(ge=0.0, le=100.0)] = Field(
        description="Proportion of language use on the internet."
    )

    praying: Optional[confloat(ge=0.0, le=100.0)] = Field(
        description="Proportion of language use for praying."
    )


class LsbqeTaskClubCodeSwitching(BaseModel):
    """Code-switching in different situations/with different groups of people."""

    parents_and_family: Optional[confloat(ge=0.0, le=100.0)] = Field(
        description="Amount of code-switching with parents and family."
    )

    friends: Optional[confloat(ge=0.0, le=100.0)] = Field(
        description="Amount of code-swithcing with friends."
    )

    social_media: Optional[confloat(ge=0.0, le=100.0)] = Field(
        description="Amount of code-switching with social media."
    )


class LsbqeTaskClub(BaseModel):
    """Community Language Use Behaviour portion of the LSBQe."""

    life_stages: LsbqeTaskClubLifeStages

    people_current: LsbqeTaskClubPeopleCurrent

    people_childhood: LsbqeTaskClubPeopleChildhood

    situations: LsbqeTaskClubSituations

    activities: LsbqeTaskClubActivities

    code_switching: LsbqeTaskClubCodeSwitching


class LsbqeTaskResponse(ResponseBase):
    """LSBQe Task Response."""

    lsb: LsbqeTaskLsb

    ldb: LsbqeTaskLdb

    club: LsbqeTaskClub

    notes: Optional[str]
