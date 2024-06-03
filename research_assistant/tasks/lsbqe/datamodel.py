"""Data model for the LSBQe Task."""

from datetime import date
from typing import Any, Hashable, Optional

from pydantic import BaseModel, Field, PastDate, StringConstraints
from typing_extensions import Annotated

from ...datamodels import patterns as p
from ...datamodels.models import ResponseBase
from ...datamodels.types import UniqueList


class LsbResidency(BaseModel):
    """Temporally limited residency of an LSBQe respondent."""

    location: Annotated[
        str, StringConstraints(strip_whitespace=True, pattern=p.LOCATION_NAME)
    ] = Field("Location (approx.) of residency.")

    start: PastDate = Field("Start date of residency.")

    end: date = Field("End date of residency.")

    def __hash__(self) -> int:
        """Return a hash computed from *location*, *start* and *end*."""
        return hash((self.location, self.start, self.end))

    def __eq__(self, other: Any) -> bool:
        """Compare two instances of `LsbResidency` for equality.

        They are considerd equal if all of *location*, *start* and *end*
        compare equal.
        """
        if isinstance(other, self.__class__):
            return (self.location, self.start, self.end) == (
                other.location,
                other.start,
                other.end,
            )
        return NotImplemented


class LsbResponse(BaseModel):
    """Language and Social Background portion of the LSBQe."""

    sex: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
            to_lower=True,
            min_length=1,
            max_length=1,
            pattern=r"^[mfoMFO]$",
        ),
    ] = Field(description="Respondent's sex/gender.")

    sex_other: Optional[
        Annotated[str, StringConstraints(strip_whitespace=True, pattern=p.SHORT_TEXT)]
    ] = Field(None, description="Description of sex/gender if sex is 'other'.")

    occupation: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1, pattern=p.SHORT_TEXT),
    ] = Field(description="Respondent's occupation.")

    handedness: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
            to_lower=True,
            min_length=1,
            max_length=1,
            pattern=r"^[rlRL]$",
        ),
    ] = Field(description="Respondent's handedness.")

    date_of_birth: PastDate = Field(description="Respondent's date of birth.")

    hearing_impairment: bool = Field(
        description="Whether respondent has a hearing impairment or not."
    )

    hearing_aid: Optional[bool] = Field(
        None,
        description="Whether a hearing aid is used, if respondent has a hearing aid.",
    )

    vision_impairment: bool = Field(
        description="Whether respondent has a vision impairment or not."
    )

    vision_aid: Optional[bool] = Field(
        None,
        description=(
            "Whether vision aids (glasses, contact lenses) are used, "
            "if respondent has a vision impairment."
        ),
    )

    vision_fully_corrected: Optional[bool] = Field(
        None, description="Whether vision aid fully corrects vision, if used."
    )

    place_of_birth: Annotated[
        str, StringConstraints(strip_whitespace=True, pattern=p.LOCATION_NAME)
    ] = Field(description="Respondent's place of birth.")

    residencies: UniqueList[LsbResidency] = Field(
        description="Respondent's past residencies over 6 month."
    )

    education_level: Annotated[int, Field(ge=1, le=5)] = Field(
        description="Respondent's education level."
    )


class LdbLanguageInformation(BaseModel):
    """Information about a language spoken by an LSBQe respondent."""

    name: Annotated[
        str, StringConstraints(strip_whitespace=True, pattern=p.LANGUAGE_NAME)
    ] = Field(description="Name of the language.")

    source_home: bool = Field(description="Whether the language was learned at home.")

    source_school: bool = Field(
        description="Whether the language was learned at school."
    )

    source_community: bool = Field(
        description="Whether the language was learned in the community."
    )

    source_other: Optional[
        Annotated[
            str,
            StringConstraints(
                strip_whitespace=True, min_length=1, pattern=p.SHORT_TEXT
            ),
        ]
    ] = Field(
        None, description="If applicable, other source(s) of language acquisition."
    )

    age: Annotated[int, Field(ge=0, le=100)] = Field(
        description="Age at which the language was acquired."
    )

    breaks: Annotated[int, Field(ge=0)] = Field(
        description="Total duration for which language was not used in months."
    )

    proficiency_speaking: Annotated[float, Field(ge=0.0, le=100.0)] = Field(
        description="Proficiency in speaking language."
    )
    proficiency_understanding: Annotated[float, Field(ge=0.0, le=100.0)] = Field(
        description="Proficiency in understanding language."
    )
    proficiency_reading: Optional[Annotated[float, Field(ge=0.0, le=100.0)]] = Field(
        None, description="Proficiency in reading language."
    )
    proficiency_writing: Optional[Annotated[float, Field(ge=0.0, le=100.0)]] = Field(
        None, description="Proficiency in writing language."
    )

    usage_speaking: Annotated[float, Field(ge=0.0, le=100.0)] = Field(
        description="Proporition of use when speaking."
    )
    usage_listening: Annotated[float, Field(ge=0.0, le=100.0)] = Field(
        description="Proportion of use when listening."
    )
    usage_reading: Optional[Annotated[float, Field(ge=0.0, le=100.0)]] = Field(
        None, description="Proportion of use when reading."
    )
    usage_writing: Optional[Annotated[float, Field(ge=0.0, le=100.0)]] = Field(
        None, description="Proportion of use when writing."
    )

    def __property_values(self) -> tuple[Hashable, ...]:
        return (
            self.name,
            self.source_home,
            self.source_community,
            self.source_other,
            self.source_school,
            self.age,
            self.breaks,
            self.proficiency_reading,
            self.proficiency_speaking,
            self.proficiency_understanding,
            self.proficiency_writing,
            self.usage_listening,
            self.usage_reading,
            self.usage_speaking,
            self.usage_writing,
        )

    def __hash__(self) -> int:
        """Return a hash computed from properties."""
        return hash(self.__property_values())

    def __eq__(self, other: Any) -> bool:
        """Compare two instances of `LdbLanguageInformation` for equality.

        They are considerd equal if all of properties
        compare equal.
        """
        if isinstance(other, self.__class__):
            return self.__property_values() == other.__property_values()
        return NotImplemented


class LdbParentInformation(BaseModel):
    """Background information about a parent."""

    parent: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True, to_lower=True, pattern=r"^(?i:mother|father)$"
        ),
    ] = Field(description="Is this for 'mother' or 'father'?")

    occupation: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1, pattern=p.SHORT_TEXT),
    ] = Field(description="Parent's occupation.")

    first_language: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1, pattern=p.LANGUAGE_NAME),
    ] = Field(description="Parent's first language.")

    second_language: Optional[
        Annotated[
            str,
            StringConstraints(
                strip_whitespace=True, min_length=1, pattern=p.LANGUAGE_NAME
            ),
        ]
    ] = Field(None, description="Parent's second language (if applicable).")

    other_languages: Optional[
        Annotated[
            str,
            StringConstraints(
                strip_whitespace=True,
                min_length=1,
            ),
        ]
    ] = Field(None, description="List of parent's other languages (if applicable).")

    def __property_values(self) -> tuple[Hashable, ...]:
        return (
            self.parent,
            self.occupation,
            self.first_language,
            self.second_language,
            self.other_languages,
        )

    def __hash__(self) -> int:
        """Return a hash computed from properties."""
        return hash(self.__property_values())

    def __eq__(self, other: Any) -> bool:
        """Compare two instances of `LdbParentInformation` for equality.

        They are considerd equal if all of properties
        compare equal.
        """
        if isinstance(other, self.__class__):
            return self.__property_values() == other.__property_values()
        return NotImplemented


class LdbResponse(BaseModel):
    """Language and Dialect Background portion of the LSBQe."""

    languages: Annotated[UniqueList[LdbLanguageInformation], Field(min_length=1)] = (
        Field(description="Languages spoken by the respondent.")
    )

    parents: Annotated[
        UniqueList[LdbParentInformation], Field(min_length=0, max_length=2)
    ] = Field(description="Information about respondent's parents.")


class ClubLifeStages(BaseModel):
    """Language use during different (early) life stages."""

    infancy_age: Annotated[float, Field(ge=0.0, le=100.0)] = Field(
        description="Proportion of language use in infancy age."
    )

    nursery_age: Annotated[float, Field(ge=0.0, le=100.0)] = Field(
        description="Proportion of language use in nursery age."
    )

    primary_age: Annotated[float, Field(ge=0.0, le=100.0)] = Field(
        description="Proportion of language use in primary school age."
    )

    secondary_age: Annotated[float, Field(ge=0.0, le=100.0)] = Field(
        description="Proportion of language use in secondary school age."
    )


class ClubPeopleCurrent(BaseModel):
    """Language use with different groups of people, currently."""

    parents: Optional[Annotated[float, Field(ge=0.0, le=100.0)]] = Field(
        None, description="Proportion of language use with parents."
    )

    children: Optional[Annotated[float, Field(ge=0.0, le=100.0)]] = Field(
        None, description="Proportion of language use with children."
    )

    siblings: Optional[Annotated[float, Field(ge=0.0, le=100.0)]] = Field(
        None, description="Proportion of language use with siblings."
    )

    grandparents: Optional[Annotated[float, Field(ge=0.0, le=100.0)]] = Field(
        None, description="Proportion of language use with grandparents."
    )

    other_relatives: Optional[Annotated[float, Field(ge=0.0, le=100.0)]] = Field(
        None, description="Proportion of language use with other relatives."
    )

    partner: Optional[Annotated[float, Field(ge=0.0, le=100.0)]] = Field(
        None, description="Proportion of language use with partner."
    )

    friends: Optional[Annotated[float, Field(ge=0.0, le=100.0)]] = Field(
        None, description="Proportion of language use with friends."
    )

    flatmates: Optional[Annotated[float, Field(ge=0.0, le=100.0)]] = Field(
        None, description="Proportion of language use with flatmates/roommates."
    )

    neighbours: Optional[Annotated[float, Field(ge=0.0, le=100.0)]] = Field(
        None, description="Proportion of language use with neighbours."
    )


class ClubPeopleChildhood(BaseModel):
    """Language use with different groups of people during childhood."""

    parents: Optional[Annotated[float, Field(ge=0.0, le=100.0)]] = Field(
        None, description="Proportion of language use with parents during childhood."
    )

    siblings: Optional[Annotated[float, Field(ge=0.0, le=100.0)]] = Field(
        None, description="Proportion of language use with siblings during childhood."
    )

    grandparents: Optional[Annotated[float, Field(ge=0.0, le=100.0)]] = Field(
        None,
        description="Proportion of language use with grandparents during childhood.",
    )

    other_relatives: Optional[Annotated[float, Field(ge=0.0, le=100.0)]] = Field(
        None,
        description="Proportion of language use with other relatives during childhood.",
    )

    friends: Optional[Annotated[float, Field(ge=0.0, le=100.0)]] = Field(
        None, description="Proportion of language use with friends during childhood."
    )

    neighbours: Optional[Annotated[float, Field(ge=0.0, le=100.0)]] = Field(
        None, description="Proportion of language use with neighbours during childhood."
    )


class ClubSituations(BaseModel):
    """Language use in different situations/settings."""

    home: Optional[Annotated[float, Field(ge=0.0, le=100.0)]] = Field(
        None, description="Proportion of language use at home."
    )

    school: Optional[Annotated[float, Field(ge=0.0, le=100.0)]] = Field(
        None, description="Proportion of language use in school."
    )

    work: Optional[Annotated[float, Field(ge=0.0, le=100.0)]] = Field(
        None, description="Proportion of language use at work."
    )

    socialising: Optional[Annotated[float, Field(ge=0.0, le=100.0)]] = Field(
        None, description="Proportion of language use when socialising."
    )

    religion: Optional[Annotated[float, Field(ge=0.0, le=100.0)]] = Field(
        None, description="Proportion of language use for religious activities."
    )

    leisure: Optional[Annotated[float, Field(ge=0.0, le=100.0)]] = Field(
        None, description="Proportion of language use for leisure activities."
    )

    commercial: Optional[Annotated[float, Field(ge=0.0, le=100.0)]] = Field(
        None, description="Proportion of language use for commercial activities."
    )

    public: Optional[Annotated[float, Field(ge=0.0, le=100.0)]] = Field(
        None, description="Proportion of language use for public affairs."
    )


class ClubActivities(BaseModel):
    """Language use for different activities."""

    reading: Optional[Annotated[float, Field(ge=0.0, le=100.0)]] = Field(
        None, description="Proportion of language use for reading."
    )

    emailing: Optional[Annotated[float, Field(ge=0.0, le=100.0)]] = Field(
        None, description="Proportion of language use for emailing."
    )

    texting: Optional[Annotated[float, Field(ge=0.0, le=100.0)]] = Field(
        None, description="Proportion of language use for texting (SMS, WhatsApp, ...)."
    )

    social_media: Optional[Annotated[float, Field(ge=0.0, le=100.0)]] = Field(
        None, description="Proportion of language use with social media."
    )

    notes: Optional[Annotated[float, Field(ge=0.0, le=100.0)]] = Field(
        None, description="Proportion of language use for notes/memos."
    )

    traditional_media: Optional[Annotated[float, Field(ge=0.0, le=100.0)]] = Field(
        None, description="Proportion of language use with traditional media."
    )

    internet: Optional[Annotated[float, Field(ge=0.0, le=100.0)]] = Field(
        None, description="Proportion of language use on the internet."
    )

    praying: Optional[Annotated[float, Field(ge=0.0, le=100.0)]] = Field(
        None, description="Proportion of language use for praying."
    )


class ClubCodeSwitching(BaseModel):
    """Code-switching in different situations/with different groups of people."""

    parents_and_family: Optional[Annotated[float, Field(ge=0.0, le=100.0)]] = Field(
        None, description="Amount of code-switching with parents and family."
    )

    friends: Optional[Annotated[float, Field(ge=0.0, le=100.0)]] = Field(
        None, description="Amount of code-swithcing with friends."
    )

    social_media: Optional[Annotated[float, Field(ge=0.0, le=100.0)]] = Field(
        None, description="Amount of code-switching with social media."
    )


class ClubResponse(BaseModel):
    """Community Language Use Behaviour portion of the LSBQe."""

    life_stages: ClubLifeStages

    people_current: ClubPeopleCurrent

    people_childhood: ClubPeopleChildhood

    situations: ClubSituations

    activities: ClubActivities

    code_switching: Optional[ClubCodeSwitching] = None


class LsbqeResponse(ResponseBase):
    """LSBQe Response."""

    lsb: LsbResponse

    ldb: LdbResponse

    club: ClubResponse

    note: Optional[str] = None
