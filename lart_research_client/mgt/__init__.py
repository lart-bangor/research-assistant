"""Data structures for the MGT (RML)."""
from email.mime import audio
from time import time, sleep
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
import os
import pathlib
from playsound import playsound

data_path: Path = config.paths.data / "MGT"
if not data_path.exists():
    data_path.mkdir(parents=True, exist_ok=True)
 
#retrieve initial info from index.html and print to file + to console
@eel.expose
def grab_mgt_ratings(data: dict[Any, Any]):
    presentime = datetime.now()
    dt_string = presentime.strftime("%d/%m/%Y %H:%M:%S")
    #currentFileLocation = pathlib.Path(__file__).parent.absolute()
    #parentFolder = currentFileLocation.parent
    #jsonLocationPath = str(parentFolder.as_posix())
    #jsonFile = jsonLocationPath + "/web/app/mgt/versions/CymEng_ENG_GB.json"
    
    try:
        with open("lart_research_client/mgt/data/dataLog.json", "a") as file:
            file.write(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> NEXT >>")
            file.write("\n\nDate & Time: " + dt_string + "\n")
        
            #file.write("\n")
            #file.write("Presentation order: ")
            #file.write(json.dumps(presentation_order))
            #file.write("\n")
            jsonOutput = json.dumps(data, indent=4)
            file.write(jsonOutput)
            
    except FileNotFoundError:
        print("\n")
        print("#########################################\n")
        print("#   The 'data' directory does not exist #\n")
        print("#########################################\n")
    print("\nMGT ratings: ")
    print(data)
    

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




   