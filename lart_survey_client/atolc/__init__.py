"""Data structures for the AToL Questionnaire (RML)."""
from typing import Any, Optional
import datetime
import sys
from datavalidator.schemas import DataSchema  # ModuleNotFoundError: No module named 'datavalidator'
from datavalidator.types import PolarT
import booteel  # ModuleNotFoundError: No module named 'lart_survey_client'
import eel
from . import patterns
from pathlib import Path 



#retrieve initial info from index.html and print to file + to console
@eel.expose
def init_atol(data: dict[Any, Any]):
    global version
    version = data.get("selectSurveyVersion")
    file = open(Path("dataLog.txt"), "w")
    file.write(fetch_atol_initial_data(data))
    file.close()
    print("Basic info from index.html: ")
    print(data)
    booteel.setlocation("atolPart1.html")

#does the same as init_atol, but for part1.html
@eel.expose
def grab_atol_ratings(data: dict[Any, Any]):
    #global version
    #version = data.get("selectSurveyVersion")
    print("AToL ratings from part1.html: ")
    print(data)

def fetch_atol_initial_data(dict):
    for key in dict:
        value = dict[key]
        print(value)
        return value

#open and read the file after the appending:
#f = open("demofile2.txt", "r")
#print(f.read())

#UNUSED set version based on values passed on from the JS in index.html
@eel.expose
def set_atol_version(data: dict[Any, Any]):
    print("full dict is ")
    print(data)
    global version
    version = data.get("selectSurveyVersion")
             
@eel.expose
def get_atol_version():
    test_version = version
    print("test version is: " + test_version)
    return test_version


    if  version == "CymEng_Eng_GB":
        title = "Language Questionnaire"
        language = "English"
        rml = "Welsh"
        instruction = "Please move the slider to record your choice."
        language_header = "The English language is..."
        rml_header = "The Welsh language is..."
        atol_header = "AToL Questionnaire (RML)"
        btn_text = "Next"
    elif version == "LmoIta_Ita_IT":
        title = "Questionario Linguistico"
        language = "Italiano"
        rml = "lombardo"
        instruction = "Si prega di spostare il cursore per registrare la propria scelta."
        language_header = "La lingua italiana è..."
        rml_header = "il lombardo è..."
        atol_header = "Questionario AToL (RML)"
        btn_text = "Avanti"

    elif version == "LtzGer_Ger_BE":
        title = "Sprachlicher Fragebogen"
        language = "Deutch"
        rml = "Moselfränkisch"
        instruction = "Bitte verwenden Sie den Schieberegler, um Ihre Auswahl aufzuzeichnen??."
        rml_header = "Moselfränkisch ist..."
        language_header = "Die deutsche Sprache ist..."
        atol_header = "AToL Fragebogen (RML)"
        btn_text = "Weiter"

    




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
        "ambiguity":    ("eindeutig",    "missverständlich"),  
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
