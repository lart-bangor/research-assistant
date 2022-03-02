"""Data structures for the Language and Social Background Questionnaire (RML)."""
from typing import Any, Optional
import datetime
import json
import sys
from datavalidator import Validator
from datavalidator.schemas import DataSchema
from datavalidator.types import EnumT, PolarT
from . import patterns

class NewResponse(DataSchema):
    """Class for representing the data of an LSBQ-RML questionnaire response."""
    __schema = {
        "id": {
            "type_": int,
            "typedesc": "LSBQ-RML Response ID",
            "constraint": (0, sys.maxsize),
        },
        "meta": {  # Meta data
            "version": {
                "type_": str,
                "typedesc": "LSBQ-RML version identifier",
                "constraint": patterns.VERSION_LABEL,
            },
            "researcher_id": {
                "type_": str,
                "typedesc": "Researcher ID",
                "constraint": patterns.SHORT_ID,
            },
            "research_location": {
                "type_": str,
                "typedesc": "location name",
                "constraint": patterns.LOCATION_NAME,
            },
            "participant_id": {
                "type_": str,
                "typedesc": "Participant ID",
                "constraint": patterns.SHORT_ID,
            },
            "consent": {
                "type_": PolarT,
                "typedesc": "consent confirmation",
                "constraint": patterns.BOOLEAN,
            },
            "date": {
                "type_": str,
                "typedesc": "current date",
                "constraint": patterns.ISO_YEAR_MONTH_DAY,
            },
        },
        "lsb": {  # Language and Social Background
            "sex": {
                "type_": EnumT,
                "typedesc": "sex",
                "constraint": patterns.SEX_TERNARY,
            },
            "sex_other": {
                "type_": str,
                "typedesc": "description of other sex",
                "constraint": patterns.SHORT_TEXT,
                "required": False,
            },
            "occupation": {
                "type_": str,
                "typedesc": "occupation",
                "constraint": patterns.SHORT_TEXT,
            },
            "handedness": {
                "type_": EnumT,
                "typedesc": "handedness",
                "constraint": patterns.HANDEDNESS,
            },
            "date_of_birth": {
                "type_": str,
                "typedesc": "date of birth",
                "constraint": patterns.ISO_YEAR_MONTH_DAY,
            },
            "hearing_impairment": {
                "type_": PolarT,
                "typedesc": "indication of hearing impairment",
                "constraint": patterns.BOOLEAN,
            },
            "hearing_aid": {
                "type_": PolarT,
                "typedesc": "indication of hearing aid use",
                "constraint": patterns.BOOLEAN,
                "required": False,
            },
            "vision_impairment": {
                "type_": PolarT,
                "typedesc": "indication of vision impairment",
                "constraint": patterns.BOOLEAN,
            },
            "vision_aid": {
                "type_": PolarT,
                "typedesc": "indication of vision aid use",
                "constraint": patterns.BOOLEAN,
                "required": False,
            },
            "vision_fully_corrected": {
                "type_": PolarT,
                "typedesc": "indication of whether vision is fully corrected",
                "constraint": patterns.BOOLEAN,
                "required": False,
            },
            "place_of_birth": {
                "type_": str,
                "typedesc": "location name for a birth place",
                "constraint": patterns.LOCATION_NAME,
            },
            "residencies_location": {
                "type_": str,
                "typedesc": "location name for place of significant residence",
                "constraint": patterns.LOCATION_NAME,
                "multiple": True,
                "required": False,
            },
            "residencies_start": {
                "type_": str,
                "typedesc": "start month and year",
                "constraint": patterns.ISO_YEAR_MONTH,
                "multiple": True,
                "required": False,
            },
            "residencies_end": {
                "type_": str,
                "typedesc": "end month and year",
                "constraint": patterns.ISO_YEAR_MONTH,
                "multiple": True,
                "required": False,
            },
            "education_level": {
                "type_": int,
                "typedesc": "education level",
                "constraint": patterns.LIKERT_5,
            },
        },
        "ldb": {  # Language and Dialect Background

        },
        "club": {  # Community Language Use Behaviour

        },
        "notes": {  # Notes
            "participant_note": {
                "type_": str,
                "typedesc": "participant note",
                "required": False,
            },
            "researcher_note": {
                "type_": str,
                "typedesc": "researcher note",
                "required": False,
            }
        },
    }

    def __init__(self, id_: Optional[int] = None):
        """Instantiates a new LSBQ-RML response object."""
        super().__init__(forcecast=True, ignorecase=True)
        if id_ is None:
            id_ = hash(self)
        self.setid(id_)

    def setmeta(self, data: dict[str, Any]) -> None:
        """Sets the metadata for the response."""
        # Fill in today's date if not supplied
        if "date" not in data or data["date"] is None:
            data["date"] = datetime.date.today().isoformat()
        super().setmeta(data)



class Response:
    """Class for representing the data of an LSBQ-RML questionnaire response."""

    __data: dict[str, dict[str, Any]]
    __instance_id: str

    def __init__(self):
        """Instantiates a new LSBQ-RML response object."""
        self.__data = {
            "meta": {   # Meta data
                "version": "",
                "researcher_id": ""
            },
            "lsb": {},  # Language and Social Background
            "ldb": {},  # Language and Dialect Background
            "club": {},  # Community Language Use Behaviour
            "notes": {}, # Notes
        }
        self.__instance_id = str(hash(self))  # Should always be unique (= memaddr + salt)

    def tojson(self) -> str:
        """Returns a JSON representation of the response."""
        return json.dumps(self.__data)

    @classmethod
    def fromjson(cls, jsonstring: str) -> "Response":
        """Returns a new Response instance constructed from JSON data."""
        data = json.loads(jsonstring)
        instance = cls()

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
        vr = Validator(forcecast=True, ignorecase=True)

        # Validate each initialisation field
        d["version"] = vr.vstr(
            "LSBQ-RML version identifier", patterns.VERSION_LABEL, version
        ).data
        d["researcher_id"] = vr.vstr(
            "Researcher ID", patterns.SHORT_ID, researcher_id
        ).data
        d["research_location"] = vr.vstr(
            "location name", patterns.LOCATION_NAME, research_location
        ).data
        d["participant_id"] = vr.vstr(
            "Participant ID", patterns.SHORT_ID, participant_id
        ).data
        d["consent"] = vr.vpolar(
            "consent confirmation", patterns.BOOLEAN, consent
        ).data
        d["date"] = vr.vstr(
            "current date", patterns.ISO_YEAR_MONTH_DAY, date
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
        vr = Validator(forcecast=True, ignorecase=True)

        # Validate each initialisation field
        d["sex"] = vr.venum(
            "sex", patterns.SEX_TERNARY, sex
        ).data
        if d["sex"] == "o":
            d["sex_other"] = vr.vstr(
                "description of other sex", patterns.SHORT_TEXT, sex_other
            ).data
        else:
            d["sex_other"] = None
        d["occupation"] = vr.vstr(
            "occupation", patterns.SHORT_TEXT, occupation
        ).data
        d["handedness"] = vr.venum(
            "handedness", patterns.HANDEDNESS, handedness
        ).data
        d["date_of_birth"] = vr.vstr(
            "date of birth", patterns.ISO_YEAR_MONTH_DAY, date_of_birth
        ).data
        d["hearing_impairment"] = vr.vpolar(
            "indication of hearing impairment", patterns.BOOLEAN, hearing_impairment
        ).data
        if d["hearing_impairment"]:
            d["hearing_aid"] = vr.vpolar(
                "indication of hearing aid use", patterns.BOOLEAN, hearing_aid
            ).data
        else:
            d["hearing_aid"] = None
        d["vision_impairment"] = vr.vpolar(
            "indication of vision impairment", patterns.BOOLEAN, vision_impairment
        ).data
        if d["vision_impairment"]:
            d["vision_aid"] = vr.vpolar(
                "indication of vision aid use", patterns.BOOLEAN, vision_aid
            ).data
            d["vision_fully_corrected"] = vr.vpolar(
                "indication of whether vision is fully corrected",
                patterns.BOOLEAN, vision_fully_corrected
            ).data
        else:
            d["vision_aid"] = None
            d["vision_fully_corrected"] = None
        d["place_of_birth"] = vr.vstr(
            "place of birth", patterns.LOCATION_NAME, place_of_birth
        ).data
        if places_of_significant_residence is not None:
            tmp: list[tuple[str, str, str]] = []
            for place_osr in places_of_significant_residence:
                tmp.append((
                    vr.vstr(
                        "place of significant residence",
                        patterns.LOCATION_NAME, place_osr[0]
                    ).data,
                    vr.vstr(
                        "start month and year", patterns.ISO_YEAR_MONTH, place_osr[1]
                    ).data,
                    vr.vstr(
                        "end month and year", patterns.ISO_YEAR_MONTH, place_osr[2]
                    ).data,
                ))
            d["places_of_significant_residence"] = tmp
        else:
            d["places_of_significant_residence"] = []
        d["education_level"] = vr.vint(
            "education level", patterns.LIKERT_5, education_level
        ).data

        # Raise exception if any of the data didn't validate
        vr.raiseif()

        # Store the data internally
        self.__data.update(d)
