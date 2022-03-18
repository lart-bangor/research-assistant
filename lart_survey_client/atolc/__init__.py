"""Data structures for the AToL Questionnaire (RML)."""
from typing import Any, Optional
import datetime
import sys
from datavalidator.schemas import DataSchema  # ModuleNotFoundError: No module named 'datavalidator'
from datavalidator.types import PolarT
import booteel  # ModuleNotFoundError: No module named 'lart_survey_client'
import eel
from . import patterns

_rating_adjectives = (
    "logical",
    "elegant",
    "fluent",
    "ambiguous",
    "appealing",
    "structured",
    "precise",
    "soft",
    "flowing",
    "beautiful",
    "systematic",
    "pleasant",
    "smooth",
    "graceful",
    "round"    
)

@eel.expose  # type: ignore
def atol_c_get_items(version):
    """Get label pairs for each AToL item depending on language selection."""
    EngVersion = {       
        "logic":    ("logical", "illogical"),
        "elegance": ("inelegant", "elegant"),
        "fluency": ("choppy", "fluent"),
        "ambiguity": ("unambiguous", "ambiguous"),
        "appeal": ("appealing", "abhorrent"),
        "structure": ("unstructured", "structured"),
        "precision": ("precise", "vague"),
        "harshness": ("harsh", "soft"),
        "flow": ("flowing", "abrupt"),
        "beauty": ("beautiful", "ugly"),
        "sistem": ("systematic", "unsystematic"),
        "pleasure": ("pleasant", "unpleasant"),
        "smoothness": ("smooth", "raspy"),
        "grace": ("clumsy", "graceful"),
        "angularity": ("angular", "round"),
              }
    ItVersion = {       
        "logic":    ("logica", "illogica"),
        "elegance": ("non elegante", "elegante"),
        "fluency": ("frammentata", "scorrevole"),
        "ambiguity": ("chiara", "ambigua"),
        "appeal": ("attraente", "ripugnante"),
        "structure": ("non strutturata", "strutturata"),
        "precision": ("precisa", "vaga"),
        "harshness": ("dura", "morbida"),
        "flow": ("fluida", "brusca"),
        "beauty": ("bella", "brutta"),
        "sistem": ("sistematica", "non sistematica"),
        "pleasure": ("piacevole", "spiacevole"),
        "smoothness": ("liscia", "ruvida"),
        "grace": ("goffa", "aggraziata"),
        "angularity": ("spigolosa", "arrotondata"),
              }
    BeVersion = {
         "logic":       ("logisch",     "unlogisch"),
        "elegance":     ("stillos",     "stilvoll"),
        "fluency":      ("stockend",    "fließend"),
        "ambiguity":    ("eindeutig",    "missverständlich"),  #something goes wrong here, and only "e" adn "i" appear in html output
        "appeal":       ("anziehend",   "abstoßend"),
        "structure":    ("stukturlos",  "sturkturiert"),
        "precision":    ("genau",       "ungenau"),
        "harshness":    ("hart",        "weich"),
        "flow": ("flüssig", "abgehackt"),
        "beauty": ("schön", "hässlich"),
        "sistem": ("systematisch", "unsystematisch"),
        "pleasure": ("angenehm", "unangenehm"),
        "smoothness": ("geschmeidig", "rau"),
        "grace": ("plump", "anmutig"),
        "angularity": ("eckig", "rund"),
    }
 
   
    if version == 'CymEng_Eng_GB':
        return EngVersion
    elif version == 'LtzGer_Ger_BE':
        return BeVersion
    elif version == 'LmoIta_Ita_IT':
        return ItVersion

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
        "language1": {
            label: {
                "type_": float,
                "typedesc": f"rating of {label}",
                "constraint": (0, 100)
            } for label in _rating_adjectives
        },
        "language2": {
            label: {
                "type_": float,
                "typedesc": f"rating of {label}",
                "constraint": (0, 100)
            } for label in _rating_adjectives
        }
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
