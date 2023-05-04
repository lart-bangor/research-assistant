"""Informed consent from user."""
import eel
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any
from .. import booteel
from ..config import config
import os
import json

#Define paths used is functions below
data_path: Path = config.paths.data / "Consent"
if not data_path.exists():
    data_path.mkdir(parents=True, exist_ok=True)

dir = os.path.dirname(os.path.realpath(__file__))
versions_dir = os.path.join(dir, "versions")
versionsDirList = os.listdir(versions_dir)


def fetch_file_info(file: str):
    """takes a json file and returns info from inside the file as a list in the form of [version_name, version_ID, version_data]"""
    file_info = []
    with open(file, encoding='utf-8') as f:
        #print("WORKING FILE is: " + file)
        data = json.load(f)
        versionId = data["meta"]["versionId"]
        versionType = data["meta"]["versionType"]
        versionLanguages = data["meta"]["versionLanguages"]
        versionName = data["meta"]["versionName"]
        file_info.extend([versionId, versionType, versionLanguages, versionName])
    #print(f"\nFile fetched: {file}. \nFile info is: {file_info}")
    return file_info


@eel.expose
def consent_getversions():
    """loops through the folder [versions] inside [consent] and finds all unique language versions, regardless of test type. 
    Returns a list of lists in the form: [versionId, languageInfo]"""
    versions = []
    versionsTracker = []
    for file_name in versionsDirList:
        if file_name[-5:] != ".json" or file_name[0] == "_":
            continue
        fileInfo = fetch_file_info(os.path.join(versions_dir, file_name))
        languageInfo = fileInfo[2]
        versionId = fileInfo[0]
        #print("\n Version found:")
        #print("\t version languages: " + languageInfo)
        #print("\t version ID: " + versionId)
        if versionsTracker.count(languageInfo) == 0:
            versionsTracker.append(languageInfo)  #keep track of the fact that you found a language version, regardless of task type
            versions.append([versionId, languageInfo])
    print(f"\nDigital consent: {len(versions)} language versions found.")
    return versions



@eel.expose
def set_options(selected_version: str):
    """Takes a language version as arg and finds all consent forms available for that version. Returns a list in the form of [version_name, version_ID, version_data]"""
    options = []
    print("Informed Consent: working DIR = ", versions_dir)
    for file_name in versionsDirList:
        bare_file_name = file_name.split(".", 1)[0]
        bare_version = selected_version.split(".", 1)[0]
        #print("bare version: " + bare_version)
        #print("bare file name: " + bare_file_name)
        if bare_file_name == bare_version:
            file_info = fetch_file_info(os.path.join(versions_dir, file_name))
            optionID = file_info[0]
            optionName = file_info[3]
            print("\n Option found:")
            print("\t option name: " + optionName)
            print("\t option ID: " + optionID)
            option = [optionID, optionName]
            options.append(option)
    #print("\nList of consent files available: ")
    #print(options)
    return options



@eel.expose
def fetch_study_info(filename: str):
    """takes a filename and returns the json data from that file"""
    file = os.path.join(versions_dir, filename)
    with open(file, "r", encoding='utf-8') as f:
        version_data = json.load(f)
    return version_data


@eel.expose
def record_consent(data: dict[Any, Any]):
    """Takes in data from index.html and prints it to file && to console."""
    presentime = datetime.now()
    dt_string = presentime.strftime("%Y-%m-%dT%H:%M:%S")
    dt_filename = str(uuid.uuid1())
    file_name = data["participantId"] + "_" + dt_filename + ".txt"
    data_file: Path = data_path / data["surveyVersion"] / file_name
    if not data_file.parent.exists():
        data_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(data_file, "a") as file:
            file.write("\n>>>>CONSENT RECORDED @: ")
            file.write(dt_string + "\n")
            for key in data:
                value = data[key]
                file.write(key + ": " + str(value) + "\n")
    except FileNotFoundError:
        print("\n")
        print("############################################\n")
        print("#   The 'consent' directory does not exist #\n")
        print("############################################\n")
    print("Consent info: ")
    print(data)
    if config.sequences.consent:
        query = booteel.buildquery({
            "selectSurveyVersion": data["surveyVersion"].split(".", 1)[0],
            "confirmConsent": str(int(data["informedConsent"])),
            "participantId": data["participantId"],
            "surveyDataForm.submit": "false",
        })
        booteel.setlocation(f"/app/{config.sequences.consent}/index.html?{query}")
    else:
        booteel.setlocation("/app/index.html")
