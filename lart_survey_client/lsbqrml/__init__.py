"""Data structures for the Language and Social Background Questionnaire (RML)."""
from typing import Any, Optional, TYPE_CHECKING
import sys
from datavalidator.schemas import DataSchema
from datavalidator.types import EnumT, PolarT
import logging
from . import patterns

logger = logging.getLogger(__name__)


class Response(DataSchema):
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
            "languages_spoken_name": {
                "type_": str,
                "typedesc": "language or dialect name",
                "constraint": patterns.LANGUAGE_NAME,
                "multiple": True,
            },
            "languages_spoken_source": {
                "type_": EnumT,
                "typedesc": "source of language acquisition",
                "constraint": patterns.ACQUISITION_SOURCE,
                "multiple": True,
            },
            "languages_spoken_source_other": {
                "type_": str,
                "typedesc": "source of language acquisition",
                "constraint": patterns.SHORT_TEXT,
                "multiple": True,
            },
            "languages_spoken_age": {
                "type_": int,
                "typedesc": "age of acquisition",
                "constraint": patterns.ACQUISITION_AGE,
                "multiple": True,
            },
            "languages_spoken_breaks": {
                "type_": int,
                "typedesc": "age of acquisition",
                "constraint": patterns.POSITIVE_NUMBER_ZERO,
                "multiple": True,
            },
            "languages_proficiency_speaking": {
                "type_": float,
                "typedesc": "indication of proficiency",
                "constraint": patterns.ANY_NUMBER,
                "multiple": True,
            },
            "languages_proficiency_understanding": {
                "type_": float,
                "typedesc": "indication of proficiency",
                "constraint": patterns.ANY_NUMBER,
                "multiple": True,
            },
            "languages_usage_speaking": {
                "type_": float,
                "typedesc": "proportion of language use",
                "constraint": patterns.ANY_NUMBER,
                "multiple": True,
            },
            "languages_usage_listening": {
                "type_": float,
                "typedesc": "proportion of language use",
                "constraint": patterns.ANY_NUMBER,
                "multiple": True,
            },
            "mother_education_level": {
                "type_": int,
                "typedesc": "education level",
                "constraint": patterns.LIKERT_5,
                "required": False,
            },
            "mother_occupation": {
                "type_": str,
                "typedesc": "occupation",
                "constraint": patterns.SHORT_TEXT,
                "required": False,
            },
            "mother_first_language": {
                "type_": str,
                "typedesc": "language or dialect name",
                "constraint": patterns.LANGUAGE_NAME,
                "required": False,
            },
            "mother_second_language": {
                "type_": str,
                "typedesc": "language or dialect name",
                "constraint": patterns.LANGUAGE_NAME,
                "required": False,
            },
            "mother_other_languages": {
                "type_": str,
                "typedesc": "list of language or dialect names",
                "constraint": patterns.LONG_TEXT,
                "required": False,
            },
            "father_education_level": {
                "type_": int,
                "typedesc": "education level",
                "constraint": patterns.LIKERT_5,
                "required": False,
            },
            "father_occupation": {
                "type_": str,
                "typedesc": "occupation",
                "constraint": patterns.SHORT_TEXT,
                "required": False,
            },
            "father_first_language": {
                "type_": str,
                "typedesc": "language or dialect name",
                "constraint": patterns.LANGUAGE_NAME,
                "required": False,
            },
            "father_second_language": {
                "type_": str,
                "typedesc": "language or dialect name",
                "constraint": patterns.LANGUAGE_NAME,
                "required": False,
            },
            "father_other_languages": {
                "type_": str,
                "typedesc": "list of language or dialect names",
                "constraint": patterns.LONG_TEXT,
                "required": False,
            },
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

    if TYPE_CHECKING:  # noqa: C901

        def setid(self, id: int) -> None:
            ...

        def getid(self) -> int:
            ...

        def setmeta(self, *args: Any) -> None:
            ...

        def getmeta(self) -> dict[str, Any]:
            ...

        def setlsb(self, *args: Any) -> None:
            ...

        def getlsb(self) -> dict[str, Any]:
            ...

        def setldb(self, *args: Any) -> None:
            ...

        def getldb(self) -> dict[str, Any]:
            ...

        def setclub(self, *args: Any) -> None:
            ...

        def getclub(self) -> dict[str, Any]:
            ...

        def setnotes(self, *args: Any) -> None:
            ...

        def getnotes(self) -> dict[str, Any]:
            ...
