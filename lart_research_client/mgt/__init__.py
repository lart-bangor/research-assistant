"""Data structures for the MGT (RML)."""
from email.mime import audio
from time import sleep
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
 

@eel.expose
def playGuise(audio):
    thisPath = str(pathlib.Path(__file__).parent.resolve())
    audiofile = thisPath + "/audio files/" + audio
    sleep(1.5)
    playsound(audiofile)

#retrieve initial info from index.html and print to file + to console
@eel.expose
def grab_mgt_ratings(data: dict[Any, Any]):
    print("data dict is: ")
    print(data)
    presentime = datetime.now()
    dt_filename = presentime.strftime("%d_%m_%Y__%H-%M-%S")
    filenameId = data["meta"]["File ID"] + "_" + dt_filename
    file_name = filenameId + ".json"
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
    print("Data returned via index.html: ")
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




   