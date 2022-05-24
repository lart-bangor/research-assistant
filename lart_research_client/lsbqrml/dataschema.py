"""Data schema implementing the LSBQ-RML questionnaire."""
import logging
import uuid
from typing import Any, Optional, TYPE_CHECKING
from ..datavalidator.schemas import DataSchema
from ..datavalidator.types import EnumT, PolarT
from . import patterns

logger = logging.getLogger(__name__)


class Response(DataSchema):
    """Class for representing the data of an LSBQ-RML questionnaire response."""
    __schema = {
        "id": {
            "type_": str,
            "typedesc": "LSBQ-RML Response ID",
            "constraint": patterns.UUID_HEX,
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
                "typedesc": "other source of language acquisition",
                "constraint": patterns.SHORT_TEXT,
                "multiple": True,
                "required": False,
            },
            "languages_spoken_age": {
                "type_": int,
                "typedesc": "age of acquisition",
                "constraint": patterns.ACQUISITION_AGE,
                "multiple": True,
            },
            "languages_spoken_breaks": {
                "type_": int,
                "typedesc": "breaks during acquisition",
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
            "infancy_age": {
                "type_": float,
                "typedesc": "proportion of language use in infancy age",
                "constraint": patterns.ANY_NUMBER,
            },
            "nursery_age": {
                "type_": float,
                "typedesc": "proportion of language use in nursery age",
                "constraint": patterns.ANY_NUMBER,
            },
            "primary_age": {
                "type_": float,
                "typedesc": "proportion of language use in primary age",
                "constraint": patterns.ANY_NUMBER,
            },
            "secondary_age": {
                "type_": float,
                "typedesc": "proportion of language use in secondary age",
                "constraint": patterns.ANY_NUMBER,
            },
            "parents": {
                "type_": float,
                "typedesc": "proportion of language use with parents",
                "constraint": patterns.ANY_NUMBER,
                "required": False,
            },
            "children": {
                "type_": float,
                "typedesc": "proportion of language use with children",
                "constraint": patterns.ANY_NUMBER,
                "required": False,
            },
            "siblings": {
                "type_": float,
                "typedesc": "proportion of language use with siblings",
                "constraint": patterns.ANY_NUMBER,
                "required": False,
            },
            "grandparents": {
                "type_": float,
                "typedesc": "proportion of language use with grandparents",
                "constraint": patterns.ANY_NUMBER,
                "required": False,
            },
            "other_relatives": {
                "type_": float,
                "typedesc": "proportion of language use with other relatives",
                "constraint": patterns.ANY_NUMBER,
                "required": False,
            },
            "partner": {
                "type_": float,
                "typedesc": "proportion of language use with partner",
                "constraint": patterns.ANY_NUMBER,
                "required": False,
            },
            "friends": {
                "type_": float,
                "typedesc": "proportion of language use with friends",
                "constraint": patterns.ANY_NUMBER,
                "required": False,
            },
            "flatmates": {
                "type_": float,
                "typedesc": "proportion of language use with flat/housemates",
                "constraint": patterns.ANY_NUMBER,
                "required": False,
            },
            "neighbours": {
                "type_": float,
                "typedesc": "proportion of language use with neighbours",
                "constraint": patterns.ANY_NUMBER,
                "required": False,
            },
            "childhood_parents": {
                "type_": float,
                "typedesc": "proportion of language use with parents in childhood",
                "constraint": patterns.ANY_NUMBER,
                "required": False,
            },
            "childhood_siblings": {
                "type_": float,
                "typedesc": "proportion of language use with siblings in childhood",
                "constraint": patterns.ANY_NUMBER,
                "required": False,
            },
            "childhood_grandparents": {
                "type_": float,
                "typedesc": "proportion of language use with grandparents in childhood",
                "constraint": patterns.ANY_NUMBER,
                "required": False,
            },
            "childhood_other_relatives": {
                "type_": float,
                "typedesc":
                    "proportion of language use with other relatives in childhood",
                "constraint": patterns.ANY_NUMBER,
                "required": False,
            },
            "childhood_friends": {
                "type_": float,
                "typedesc": "proportion of language use with friends in childhood",
                "constraint": patterns.ANY_NUMBER,
                "required": False,
            },
            "childhood_neighbours": {
                "type_": float,
                "typedesc": "proportion of language use with neighbours in childhood",
                "constraint": patterns.ANY_NUMBER,
                "required": False,
            },
            "home": {
                "type_": float,
                "typedesc": "proportion of language use at home",
                "constraint": patterns.ANY_NUMBER,
                "required": False,
            },
            "school": {
                "type_": float,
                "typedesc": "proportion of language use at school",
                "constraint": patterns.ANY_NUMBER,
                "required": False,
            },
            "work": {
                "type_": float,
                "typedesc": "proportion of language use at work",
                "constraint": patterns.ANY_NUMBER,
                "required": False,
            },
            "socialising": {
                "type_": float,
                "typedesc": "proportion of language use when socialising",
                "constraint": patterns.ANY_NUMBER,
                "required": False,
            },
            "religion": {
                "type_": float,
                "typedesc": "proportion of language use for religion",
                "constraint": patterns.ANY_NUMBER,
                "required": False,
            },
            "leisure": {
                "type_": float,
                "typedesc": "proportion of language use for leisure activities",
                "constraint": patterns.ANY_NUMBER,
                "required": False,
            },
            "commercial": {
                "type_": float,
                "typedesc": "proportion of language use for commercial activities",
                "constraint": patterns.ANY_NUMBER,
                "required": False,
            },
            "public": {
                "type_": float,
                "typedesc": "proportion of language use for public affairs",
                "constraint": patterns.ANY_NUMBER,
                "required": False,
            },
            "reading": {
                "type_": float,
                "typedesc": "proportion of language use for reading",
                "constraint": patterns.ANY_NUMBER,
                "required": False,
            },
            "emailing": {
                "type_": float,
                "typedesc": "proportion of language use for emailing",
                "constraint": patterns.ANY_NUMBER,
                "required": False,
            },
            "texting": {
                "type_": float,
                "typedesc": "proportion of language use for texting",
                "constraint": patterns.ANY_NUMBER,
                "required": False,
            },
            "social_media": {
                "type_": float,
                "typedesc": "proportion of language use for social media",
                "constraint": patterns.ANY_NUMBER,
                "required": False,
            },
            "notes": {
                "type_": float,
                "typedesc": "proportion of language use for notes",
                "constraint": patterns.ANY_NUMBER,
                "required": False,
            },
            "traditional_media": {
                "type_": float,
                "typedesc": "proportion of language use for traditional media",
                "constraint": patterns.ANY_NUMBER,
                "required": False,
            },
            "internet": {
                "type_": float,
                "typedesc": "proportion of language use for internet",
                "constraint": patterns.ANY_NUMBER,
                "required": False,
            },
            "praying": {
                "type_": float,
                "typedesc": "proportion of language use for praying",
                "constraint": patterns.ANY_NUMBER,
                "required": False,
            },
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

    def __init__(self, id_: Optional[str] = None):
        """Instantiates a new LSBQ-RML response object."""
        super().__init__(forcecast=True, ignorecase=True)
        if id_ is None:
            id_ = str(uuid.uuid1())
        self.setid(id_)

    if TYPE_CHECKING:  # noqa: C901

        def setid(self, id: str) -> None:
            """Set the id of the LSBQ-RML instance."""
            ...

        def getid(self) -> str:
            """Get the id of the LSBQ-RML instance."""
            ...

        def setmeta(self, *args: Any) -> None:
            """Set the meta data of the LSBQ-RML instance."""
            ...

        def getmeta(self) -> dict[str, Any]:
            """Get the meta data of the LSBQ-RML instance."""
            ...

        def setlsb(self, *args: Any) -> None:
            """Set the landuage and social background data of the LSBQ-RML instance."""
            ...

        def getlsb(self) -> dict[str, Any]:
            """Get the landuage and social background data of the LSBQ-RML instance."""
            ...

        def setldb(self, *args: Any) -> None:
            """Set the landuage and dialect background data of the LSBQ-RML instance."""
            ...

        def getldb(self) -> dict[str, Any]:
            """Get the landuage and dialect background data of the LSBQ-RML instance."""
            ...

        def setclub(self, *args: Any) -> None:
            """Set the community language use behaviour data of the LSBQ-RML instance."""
            ...

        def getclub(self) -> dict[str, Any]:
            """Get the community language use behaviour data of the LSBQ-RML instance."""
            ...

        def setnotes(self, *args: Any) -> None:
            """Set the notes data of the LSBQ-RML instance."""
            ...

        def getnotes(self) -> dict[str, Any]:
            """Get the notes data of the LSBQ-RML instance."""
            ...
