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

#EngCym_GB.atolc.json
@eel.expose
def set_options(selected_version: str):
    """Takes a language version as arg and finds all consent forms available for that version. Retursn a list in teh form of [version_name, version_data]"""
    print("My version: " + selected_version + str(type(selected_version))) 
    options = []
    dir = os.listdir()
    dir = os.listdir('research_client\\consent\\versions')
    for file_name in dir:
        bare_file_name = file_name.split(".", 1)[0]
        if bare_file_name == selected_version:
            options.append(file_name)
    print("final list = ")
    print(options)
    return options



@eel.expose
def fetch_study_info(filename: str):
    file = 'research_client\\consent\\versions\\' + filename
    with open(file, "r") as f:
        version_data = json.load(f)
        #print(version_data)
    return version_data


@eel.expose
def record_consent(data: dict[Any, Any]):
    """Retrieve consent from partInformed.html and print to file + to console."""
    presentime = datetime.now()
    dt_string = presentime.strftime("%Y-%m-%dT%H:%M:%S")
    dt_filename = str(uuid.uuid1())
    file_name = data["partId"] + "_" + dt_filename + ".txt"
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
            "participantId": data["partId"],
            "surveyDataForm.submit": "false",
        })
        booteel.setlocation(f"/app/{config.sequences.consent}/index.html?{query}")
    else:
        booteel.setlocation("/app/index.html")
