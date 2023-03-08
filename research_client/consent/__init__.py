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

data_path: Path = config.paths.data / "Consent"
if not data_path.exists():
    data_path.mkdir(parents=True, exist_ok=True)

dir = os.path.dirname(os.path.realpath(__file__))
versions_dir = dir + "\\versions\\"

@eel.expose
def set_options(selected_version: str):
    """Takes a language version as arg and finds all consent forms available for that version. Returns a list in the form of [version_name, version_ID, version_data]"""
    versionsDirList = os.listdir(dir + '\\versions')
    options = []
    print("Informed Consent: working DIR = " + dir)
    for file_name in versionsDirList:
        bare_file_name = file_name.split(".", 1)[0]
        if bare_file_name == selected_version:
            with open(versions_dir + file_name, encoding='utf-8') as f:
                data = json.load(f)
                optionName = data["meta"]["versionName"]
                optionID = data["meta"]["versionId"]
                print("\n Option found:")
                print("\t option name: " + optionName)
                print("\t option ID: " + optionID)
                option = [optionID, optionName]
                options.append(option)
    print("\nList of consent files available: ")
    print(options)
    return options



@eel.expose
def fetch_study_info(filename: str):
    file = versions_dir + filename
    with open(file, "r") as f:
        version_data = json.load(f)
    return version_data


@eel.expose
def record_consent(data: dict[Any, Any]):
    """Retrieve consent from partInformed.html and print to file + to console."""
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
            "selectSurveyVersion": data["surveyVersion"],
            "confirmConsent": int(data["informedConsent"]),
            "participantId": data["participantId"],
            "surveyDataForm.submit": "false",
        })
        booteel.setlocation(f"/app/{config.sequences.consent}/index.html?{query}")
    else:
        booteel.setlocation("/app/index.html")
