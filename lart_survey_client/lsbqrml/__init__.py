"""Data structures for the Language and Social Background Questionnaire (RML)."""
from typing import Any, Optional
import datetime
from datavalidator import DataValidator


class Pattern:
    """Class collating patterns/ranges that are required by different question types."""
    DATE: str = r"[0-9]{1,4}\-(0?[1-9]|1[0-2])\-(0?[1-9]|[12][0-9]|3[01])"  # YYYY-MM-DD
    MONTH_YEAR: str = r"[0-9]{1,4}\-(0?[1-9]|1[0-2])"  # YYYY-MM
    MONTH: str = r"(0?[1-9]|1[0-2])"  # MM
    POLARITY: tuple[set[Any], set[Any]] = (
        {True,  "true",  "on",  "yes", 1, "1"},  # positive/true
        {False, "false", "off", "no",  0, "0"},  # negative/false
    )
    IDENTIFIER: str = r"[A-Za-z0-9]{3,10}"
    LOCATION_NAME: str = r"[A-Za-z0-9, \(\)]{1,50}"
    VERSION_LABEL: str = r"\w{13, 17}"
    SEX: str = r"[mMfFoO]"  # male, female, other
    SHORT_TEXT: str = r".{3,255}"
    LONG_TEXT: str = r".*"
    HANDEDNESS: str = r"[lLrRaA]"  # left, right, ambidextrous
    EQF_LEVEL: tuple[int, int] = (1, 8)
    EDUCATION_5_SCALE: tuple[int, int] = (1, 5)  # EQF 1, 2-3, 4, 5-6, 7-8
    ACQUISITION_SOURCE: str = r"[hHsScCoO]"  # home, school, community, other
    LANGUAGE_NAME: str = r"\w{3,50}"  # Are there any shorter than 3 (Ido)?
    CONTINUOUS_RANGE: tuple[float, float] = (0.0, 1.0)


class Response:
    """Class for representing the data of an LSBQ-RML questionnaire response."""

    __data: dict[str, Any] = {}
    __instance_id: str

    def __init__(self):
        """Instantiates a new LSBQ-RML response object."""
        global instances
        self.__instance_id = str(hash(self))  # Should always be unique (= memaddr + salt)

    def getid(self) -> str:
        """Returns the unique instance id of the Response object."""
        return self.__instance_id

    def setmeta(
        self,
        version: str,
        researcher_id: str,
        research_location: str,
        participant_id: str,
        consent: bool,
        date: Optional[str] = None
    ) -> None:
        """Sets the metadata for the response."""
        # Fill in today's date if not supplied
        if date is None:
            date = datetime.date.today().isoformat()

        # Set up a data buffer and a validator
        d: dict[str, Any] = {}
        vr = DataValidator(forcecast=True)

        # Validate each initialisation field
        d["version"] = vr.validatestring(
            "LSBQ-RML version identifier", Pattern.VERSION_LABEL, version
        ).data
        d["researcher_id"] = vr.validatestring(
            "Researcher ID", Pattern.IDENTIFIER, researcher_id
        ).data
        d["research_location"] = vr.validatestring(
            "location name", Pattern.LOCATION_NAME, research_location
        ).data
        d["participant_id"] = vr.validatestring(
            "Participant ID", Pattern.IDENTIFIER, participant_id
        ).data
        d["consent"] = vr.validatebool(
            "consent confirmation",
            Pattern.POLARITY,
            consent, softcast=True, forcecast=False
        ).data
        d["date"] = vr.validatestring(
            "current date",
            Pattern.DATE,
            date
        )

        # Raise exception if any of the data didn't validate
        vr.raiseif()

        # Store the data internally
        self.__data.update(d)

    def setlsb(
        self,
        sex: str,
        sex_other: Optional[str],
        occupation: str,
        handedness: str,
        date_of_birth: str,
        hearing_impairment: bool,
        hearing_aid: Optional[bool],
        vision_impairment: bool,
        vision_aid: Optional[bool],
        vision_fully_corrected: Optional[bool],
        place_of_birth: str,
        places_of_significant_residence: Optional[list[tuple[str, str, str]]],
        education_level: int
    ) -> None:
        """Sets the data from the Language and Social Background section."""
        # Set up a data buffer and a validator
        d: dict[str, Any] = {}
        vr = DataValidator(forcecast=True)

        # Validate each initialisation field
        d["sex"] = vr.validatestring(
            "sex", Pattern.SEX, sex
        ).data.lower()
        if d["sex"] == "o":
            d["sex_other"] = vr.validatestring(
                "description of other sex", Pattern.SHORT_TEXT, sex_other
            ).data
        else:
            d["sex_other"] = None
        d["occupation"] = vr.validatestring(
            "occupation", Pattern.SHORT_TEXT, occupation
        ).data
        d["handedness"] = vr.validatestring(
            "handedness", Pattern.HANDEDNESS, handedness
        ).data.lower()
        d["date_of_birth"] = vr.validatestring(
            "date of birth", Pattern.DATE, date_of_birth
        ).data
        d["hearing_impairment"] = vr.validatebool(
            "indication of hearing impairment",
            Pattern.POLARITY,
            hearing_impairment, softcast=True, forcecast=False
        ).data
        if d["hearing_impairment"]:
            d["hearing_aid"] = vr.validatebool(
                "indication of hearing aid use",
                Pattern.POLARITY,
                hearing_aid, softcast=True, forcecast=False
            ).data
        else:
            d["hearing_aid"] = None
        d["vision_impairment"] = vr.validatebool(
            "indication of vision impairment",
            Pattern.POLARITY,
            vision_impairment, softcast=True, forcecast=False
        ).data
        if d["vision_impairment"]:
            d["vision_aid"] = vr.validatebool(
                "indication of vision aid use",
                Pattern.POLARITY,
                vision_aid, softcast=True, forcecast=False
            ).data
            d["vision_fully_corrected"] = vr.validatebool(
                "indication of whether vision is fully corrected",
                Pattern.POLARITY,
                vision_fully_corrected, softcast=True, forcecast=False
            ).data
        else:
            d["vision_aid"] = None
            d["vision_fully_corrected"] = None
        d["place_of_birth"] = vr.validatestring(
            "place of birth", Pattern.LOCATION_NAME, place_of_birth
        ).data
        if places_of_significant_residence is not None:
            tmp: list[tuple[str, str, str]] = []
            for place_osr in places_of_significant_residence:
                tmp.append((
                    vr.validatestring(
                        "place of significant residence",
                        Pattern.LOCATION_NAME,
                        place_osr[0]
                    ).data,
                    vr.validatestring(
                        "month and year", Pattern.MONTH_YEAR, place_osr[1]
                    ).data,
                    vr.validatestring(
                        "month and year", Pattern.MONTH_YEAR, place_osr[2]
                    ).data,
                ))
            d["places_of_significant_residence"] = tmp
        else:
            d["places_of_significant_residence"] = []
        d["education_level"] = vr.validateint(
            "education level", Pattern.EDUCATION_5_SCALE, education_level
        ).data

        # Raise exception if any of the data didn't validate
        vr.raiseif()

        # Store the data internally
        self.__data.update(d)
