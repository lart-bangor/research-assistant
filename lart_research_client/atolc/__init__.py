"""Data structures for the AToL Questionnaire (RML)."""
import eel
import json
import random
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from .. import booteel
from ..config import config
from ..datavalidator.schemas import DataSchema
from ..datavalidator.types import PolarT
from . import patterns


data_path: Path = config.paths.data / "AToL-C"
if not data_path.exists():
    data_path.mkdir(parents=True, exist_ok=True)

presentime = datetime.now()
dt_string = presentime.strftime("%d/%m/%Y %H:%M:%S")
dt_filename = presentime.strftime("%d_%m_%Y__%H-%M-%S")

@eel.expose
def init_atol(data: dict[Any, Any]):
    """Retrieve initial info from index.html and print to file + to console."""
    global version
    version = data.get("selectSurveyVersion")
    file_name = data.get("participantId") + "_" + dt_filename + ".txt"
    data_file = data_path / file_name

    try:
        with open(data_file, "a") as fp:
            fp.write(f"\nDate & Time: {dt_string}\n")
            for key in data:
                value = data[key]
                fp.write(f"{key}: {str(value)}\n")
            fp.write("\n")
    except FileNotFoundError:
        print("\n")
        print("##############################################\n")
        print("# ERROR: The 'data' directory does not exist #\n")
        print("##############################################\n")
    print("Basic info from index.html: ")
    print(data)
    booteel.setlocation("atolRatingsMaj.html")


@eel.expose
def grab_atol_ratings(data: dict[Any, Any], source, version, partId):
    """Does the same as init_atol, but for part1.html."""
    location = fetch_location(source, version)
    file_name = partId + "_" + dt_filename + ".txt"
    data_file = data_path / file_name
    presentation_order = key_list(data) #record order in which data was presented and output labels
    data = alphabetise(data)  #now reset data in alphabetical order ready for writing to file

    try:
        with open(data_file, "a") as fp:
            fp.write("Presentation Order: ")
            fp.write(json.dumps(presentation_order))
            fp.write("\nRatings:\n")
            for key in data:
                value = data[key]
                fp.write(f"    {key}: {str(value)}\n")
            fp.write("\n")
    except FileNotFoundError:
        print("The 'data' directory does not exist")
    print("AToL ratings from " + source + ".html: ")
    print(data)
    booteel.setlocation(location)


def fetch_location(source_file, version):
    if 'Maj' in source_file:
        return "atolRatingsRml.html"
    elif 'Rml' in source_file:
        length = len(version)
        locationLabel = length - 2
        suffix = version[locationLabel:]
        return "atolEnd_" + suffix + ".html"
    else:
        print("ERROR: no such file")


def randomize(dictionary):
    randomized_version = {}
    items = list(dictionary.items())  # List of tuples of (key,values)
    random.shuffle(items)

    for key, value in items:
        randomized_version[key] = value
        print(key, ":", value)
    return randomized_version


def alphabetise(dictionary):
    alphabetised_dict = {}
    
    for key, value in sorted(dictionary.items()):
        alphabetised_dict[key] = value
    return alphabetised_dict


def key_list(dic):
    list_of_keys = []
    for key in dic:
        list = key.rsplit("_")  #split list at each underscore
        clean = list[-1]        #find last item on split tlist
        list_of_keys.append(clean)
    return list_of_keys


#@eel.expose
#def get_atol_version():
    #test_version = version
    #print("test version is: " + test_version)
    #return test_version


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
        "logic":        ("logical", "illogical"),
        "elegance":     ("inelegant", "elegant"),
        "fluency":      ("choppy", "fluent"),
        "ambiguity":    ("unambiguous", "ambiguous"),
        "appeal":       ("appealing", "abhorrent"),
        "structure":    ("unstructured", "structured"),
        "precision":    ("precise", "vague"),
        "harshness":    ("harsh", "soft"),
        "flow":         ("flowing", "abrupt"),
        "beauty":       ("beautiful", "ugly"),
        "sistem":       ("systematic", "unsystematic"),
        "pleasure":     ("pleasant", "unpleasant"),
        "smoothness":   ("smooth", "raspy"),
        "grace":        ("clumsy", "graceful"),
        "angularity":   ("angular", "round"),
              }
    ItVersion = {       
        "logic":        ("logica", "illogica"),
        "elegance":     ("non elegante", "elegante"),
        "fluency":      ("frammentata", "scorrevole"),
        "ambiguity":    ("chiara", "ambigua"),
        "appeal":       ("attraente", "ripugnante"),
        "structure":    ("non strutturata", "strutturata"),
        "precision":    ("precisa", "vaga"),
        "harshness":    ("dura", "morbida"),
        "flow":         ("fluida", "brusca"),
        "beauty":       ("bella", "brutta"),
        "sistem":       ("sistematica", "non sistematica"),
        "pleasure":     ("piacevole", "spiacevole"),
        "smoothness":   ("liscia", "ruvida"),
        "grace":        ("goffa", "aggraziata"),
        "angularity":   ("spigolosa", "arrotondata"),
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
        "flow":         ("flüssig", "abgehackt"),
        "beauty":       ("schön", "hässlich"),
        "sistem":       ("systematisch", "unsystematisch"),
        "pleasure":     ("angenehm", "unangenehm"),
        "smoothness":   ("geschmeidig", "rau"),
        "grace":        ("plump", "anmutig"),
        "angularity":   ("eckig", "rund"),
    }


    if version == 'CymEng_Eng_GB':
        output = EngVersion
    elif version == 'LtzGer_Ger_BE':
        output = BeVersion
    elif version == 'LmoIta_Ita_IT':
        output = ItVersion

    return randomize(output)


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
