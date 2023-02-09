"""Data structures for the AToL Questionnaire (RML)."""
import eel
import json
import random
import sys
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, Iterable, final
from .. import booteel
from ..config import config
from ..datavalidator.schemas import DataSchema
from ..datavalidator.types import PolarT
from . import patterns
from collections import OrderedDict
import os, glob

data_path: Path = config.paths.data / "AToL-C"
if not data_path.exists():
    data_path.mkdir(parents=True, exist_ok=True)

presentime = datetime.now()
dt_string = presentime.strftime("%d/%m/%Y %H:%M:%S")
dt_filename = presentime.strftime("%d_%m_%Y__%H-%M-%S")

##This works in that it gets the versions from json, but can't get it to work with 
##the <options> dropdown as I can't work out where the ID would come from...
##so currently this fucntion is not called anywhere
@eel.expose
def atol_getversions():
    absolute_path = os.path.abspath(__file__)
    vers_path = os.path.dirname(absolute_path) + "\\versions"
    versions = []

    for filename in glob.glob(os.path.join(vers_path, '*.json')):
        with open(os.path.join(os.getcwd(), filename), 'r') as f:
            vers_data = json.load(f)
            this_version = vers_data["meta"]["versionName"]
            versions.append(this_version)
            print(this_version)
    return versions


def arrange_data(data):
    ordered_data = OrderedDict(data)
    ordered_data.update({"Date_&_Time": dt_string})
    ordered_data.move_to_end("Date_&_Time", last=False)
    finalDict = {
        "meta": ordered_data}
    return finalDict
    

def get_id(dict):
    id = dict["participantId"] + "_" + dt_filename
    return id

@eel.expose
def init_atol(myData: dict[str, str]) -> None:
    """Retrieve initial info from index.html and print to file + to console."""
    global version
    version = myData["selectSurveyVersion"]
    file_name = get_id(myData) + ".json"
    data = arrange_data(myData)
    data_file = data_path / file_name
    
    try:
        with open(data_file, "a") as fp:
            json_output = json.dumps(data, indent=4)
            fp.write(json_output)
    except FileNotFoundError:
        print("\n")
        print("##############################################\n")
        print("# ERROR: The 'data' directory does not exist #\n")
        print("##############################################\n")
    print("Basic info from index.html: ")
    print(data)
    booteel.setlocation("atolRatingsMaj.html")

def arrange_order(dict, source):
    presentation_order = key_list(dict) #record order in which data was presented
    print("presentable type is")
    print(type(presentation_order))
    presentable= alphabetise(dict)  #now reset data in alphabetical order ready for writing to file
    presOrderLabel = "presentation order_" + source
    ratingsLabel = "Ratings_" + source
    finalDict = {
        presOrderLabel: presentation_order,
        ratingsLabel : presentable
    }
    return finalDict
             

@eel.expose
def grab_atol_ratings(myData: dict[Any, Any], source: str, version: str, partId: str):
    """Does the same as init_atol, but for ratings"""
    location = fetch_location(source, version)
    file_name = partId + "_" + dt_filename + ".json"
    data_file = data_path / file_name
    data = arrange_order(myData, source)
    
    try:
        with open(data_file, 'r') as fin:
            current_data = json.load(fin)
            current_data.update(data)
            #full_data = current_data
    except FileNotFoundError as exc:
        pass
            
    try:
        with open(data_file, 'w') as fout:
            json_output = json.dumps(current_data, indent=4)
            fout.write(json_output)
    except FileNotFoundError:
        print("The 'data' directory does not exist")
    print("AToL ratings from " + source + ".html: ")
    print(data)
    booteel.setlocation(location)


def fetch_location(source_file: str, version: str) -> Optional[str]:
    """Get the name for atolEnd file."""
    if 'Maj' in source_file:
        return "atolRatingsRml.html"
    elif 'Rml' in source_file:
        #length = len(version)
        #locationLabel = length - 2
        #suffix = version[locationLabel:]
        return "atolEnd.html"
    else:
        print("fetch_location() in __init__.py says: ERROR: no such file")


def randomize(dictionary: dict[str, Any]) -> dict[str, Any]:
    """Return a dict in randomized order."""
    randomized_version = {}
    items = list(dictionary.items())  # List of tuples of (key,values)
    random.shuffle(items)

    for key, value in items:
        randomized_version[key] = value
        print(key, ":", value)
    return randomized_version


def alphabetise(dictionary: dict[str, Any]) -> dict[str, Any]:
    """Return a dict in alphabetised order."""
    alphabetised_dict = {}

    for key, value in sorted(dictionary.items()):
        alphabetised_dict[key] = value
    return alphabetised_dict


def key_list(dic: dict[str, Any]) -> Iterable[Any]:
    """Return the keys of a dictionary."""
    list_of_keys = []
    for key in dic:
        list = key.rsplit("_")  # split list at each underscore
        clean = list[-1]        # find last item on split tlist
        list_of_keys.append(clean)
    return list_of_keys

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
def atol_c_get_items(version: str) -> Optional[dict[str, tuple[str, str]]]:
    """Get label pairs for each AToL item depending on language selection."""
    directory = os.path.abspath(os.getcwd()) + "\\lart_research_client\\atolc"
    version_file = directory + "\\versions\\" + version + ".json"
    atol_items = []
    with open(version_file, encoding='utf-8') as f:
        atol_stim = json.load(f)
        stim_list = atol_stim['adjectives']
        intface = atol_stim['intface_info']
        rand_list = randomize(stim_list)
        atol_items.append(intface)
        atol_items.append(rand_list)
        return atol_items


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
        super().setmeta(data)                                                   # type: ignore

    if TYPE_CHECKING:

        def setid(self, id_: str) -> None:
            """Set the ID field of the Response."""
            ...
