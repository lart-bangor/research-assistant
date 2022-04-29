"""Informed consent from user."""
import eel
import json
from datetime import datetime
from pathlib import Path
from typing import Any
from .. import booteel
from ..config import config


@eel.expose
def record_consent(data: dict[Any, Any]):
    """Retrieve consent from partInformed.html and print to file + to console."""
    presentime = datetime.now()
    dt_string = presentime.strftime("%d/%m/%Y %H:%M:%S")
    try:
        with open("lart_research_client/consent/consentLog.txt", "a") as file:
            file.write("\n>>>>CONSENT RECORDED @: ")
            file.write(dt_string + "\n")
            for key in data:
                value = data[key]
                file.write(key + ": " + str(value) + "\n")
    except FileNotFoundError:
        print("\n")
        print("#########################################\n")
        print("#   The 'consent' directory does not exist #\n")
        print("#########################################\n")
    print("Consent info: ")
    print(data)
    booteel.setlocation("../index.html")