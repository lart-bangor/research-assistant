"""Data structures for the Language and Social Background Questionnaire (RML)."""
from typing import Any, Optional
import datetime
import sys
from datavalidator.schemas import DataSchema
from datavalidator.types import EnumT, PolarT
from . import patterns

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
            "languages_spoken": {
                "type_": str,
                "typedesc": "language",
                "constraint": patterns.SHORT_TEXT,
                "multiple": True,
                "required": True,
            }
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

    # def setmeta(self, data: dict[str, Any]) -> None:
    #     """Sets the metadata for the response."""
    #     # Fill in today's date if not supplied
    #     if "date" not in data or data["date"] is None:
    #         data["date"] = datetime.date.today().isoformat()
    #     print("Setting metadata:", data)
    #     super().setmeta(data)