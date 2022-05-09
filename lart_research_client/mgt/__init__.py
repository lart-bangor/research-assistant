"""Data structures for the MGT (RML)."""
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

#retrieve initial info from index.html and print to file + to console
@eel.expose
def init_mgt(data: dict[Any, Any]):
    global version
    version = data.get("selectSurveyVersion")
    presentime = datetime.now()
    dt_string = presentime.strftime("%d/%m/%Y %H:%M:%S")
    try:
        with open("lart_research_client/mgt/data/dataLog.txt", "a") as file:
            file.write(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> NEXT >>")
            file.write("\n\nDate & Time: " + dt_string + "\n")
            for key in data:
                value = data[key]
                file.write(key + ": " + str(value) + "\n")
    except FileNotFoundError:
        print("\n")
        print("#########################################\n")
        print("#   The 'data' directory does not exist #\n")
        print("#########################################\n")
    print("Basic info from index.html: ")
    print(data)
    booteel.setlocation("mgtRatings.html")

#does the same as init_atol, but for part1.html
@eel.expose
def grab_mgt_ratings(data: dict[Any, Any], source, version):
    location = fetch_location(source, version)
    presentation_order = key_list(data) #record order in which data was presented and output labels
    data = alphabetise(data)  #now reset data in alphabetical order ready for writing to file
       
    try:
        with open("lart_survey_client/atolc/data/dataLog.txt", "a") as file:
            file.write("\n")
            file.write("Presentation order: ")
            file.write(json.dumps(presentation_order))
            file.write("\n")
            for key in data:
                value = data[key]
                file.write(key + ": " + str(value) + "\n")
            file.write("\n")

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



 

@eel.expose  # type: ignore
def mgt_get_items(version):
    """Get label pairs for each AToL item depending on language selection."""
    EngVersion = {       
        "logic":        ("ugly", "beautiful"),
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

   