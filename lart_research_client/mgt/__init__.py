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

 
#retrieve initial info from index.html and print to file + to console
@eel.expose
def init_mgt(data: dict[Any, Any]):
    presentime = datetime.now()
    dt_string = presentime.strftime("%d/%m/%Y %H:%M:%S")
    #currentFileLocation = pathlib.Path(__file__).parent.absolute()
    #parentFolder = currentFileLocation.parent
    #jsonLocationPath = str(parentFolder.as_posix())
    #jsonFile = jsonLocationPath + "/web/app/mgt/versions/CymEng_ENG_GB.json"
    
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
    
#fetches ratings from mgtRatings.html
@eel.expose
def grab_mgt_ratings(data: dict[Any, Any], source, version):
    fetchCurrentGuise()
#    global mgtAudioList, guise_counter
    #presentation_order = key_list(data)        #record order in which data was presented and output labels
    data = alphabetise(data)                    #now reset data in alphabetical order ready for writing to file
    
    #check if there are guises left to play [they play via playGuise(), called in JS]
 #   if guise_counter < (len(mgtAudioList)): ##if there are still items on the list:
  #      mgtAudioList.pop(0)                 #remove current 1st item from list
   #     nxtLocation = "mgtRatings.html"     #and set next page to _self
    #    guise_counter +=1                   #reset counter
   # else:
    #    mgtAudioList.pop(0)
    #    nxtLocation = "mgtEnd.html"         #else, display thank you page and end MGT

   # print("\n" + "mgtAudioLIst now is: " + str(mgtAudioList))
   
    #record user respponses for guise
    try:
        with open("lart_research_client/mgt/data/dataLog.txt", "a") as file:
            #file.write("\n")
            #file.write("Presentation order: ")
            #file.write(json.dumps(presentation_order))
            #file.write("\n")
            for key in data:
                value = data[key]
                file.write(key + ": " + str(value) + "\n")
            file.write("\n")

    except FileNotFoundError:
        print("!!!The 'data' directory does not exist!!!")
    print("\nMGT ratings from " + source + ".html: ")
    print(data)
    
    # booteel.setlocation(nxtLocation)

@eel.expose
def playGuise():
    currentFileLocation = pathlib.Path(__file__).parent.absolute()
    audioLocationPath = str(currentFileLocation.as_posix())
#    audioFile = audioLocationPath + "/audio files/" + mgtAudioList[0]
    sleep(1.5)
 #   print("\ncurrently playing...:" + mgtAudioList[0])
#    playsound(audioFile , block = False)

@eel.expose
def fetchCurrentGuise():               #return name of guise being played, but without extension
    global mgtAudioList
    currentAudio = str(mgtAudioList[0])
    extensionBegin = currentAudio.find(".")
    guiseName = currentAudio[0:extensionBegin]
    return guiseName


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




   