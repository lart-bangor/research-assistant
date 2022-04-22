"""Exposes the LSBQ-RML to Python Eel."""
import eel
import re
from typing import Optional, Union, Callable, Any, TypeVar, cast
from pathlib import Path
from functools import wraps
from lsbqrml import Response, logger
from lsbqrml.versions import versions
import datetime
from copy import copy
from datavalidator.exceptions import DataValidationError
from config import config
import booteel
import json
from urllib.parse import quote as urlquote

# TypeVar for function wrappers
F = TypeVar("F", bound=Callable[..., Any])

# Function to be called to handle exceptions, or None to not handle exceptions
exceptionhandler: Optional[Callable[..., None]] = None

# Keeps track of current Response instances
instances: dict[str, Response] = {}


def _getinstance(instid: str) -> Response:
    if not isinstance(instid, str):  # type: ignore
        instid = str(instid)
    if instid not in instances:
        raise AttributeError(f"No current response instance with instid `{instid}`.")
    return instances[instid]


def _handleexception(exc: Exception) -> None:
    """Passes exception to exceptionhandler if defined, otherwise continues raising."""
    logger.exception(exc)
    if exceptionhandler is not None:
        exceptionhandler(exc)
    else:
        raise exc


def _expose(func: F) -> F:
    """Wraps, renames and exposes a function to eel."""
    @wraps(func)
    def api_wrapper(
        *args: list[Any],
        **kwargs: dict[str, Any]
    ) -> Optional[Union[F, bool]]:
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            if isinstance(exc, DataValidationError):
                booteel.modal(
                    "Data Validation Error",
                    exc.validator.tohtml(errorsonly=True)
                )
                _handleexception(exc)
            else:
                booteel.displayexception(exc)
                _handleexception(exc)
            return False
    eel._expose("_lsbqrml_" + func.__name__, api_wrapper)  # type: ignore
    return cast(F, api_wrapper)


@_expose
def load_version(instid: str, sections: list[str]) -> dict[str, dict[str, Any]]:
    """Load specified sections of an LSBQ-RML version implementation."""
    logger.info(f"Retrieving version data for LSBQ-RML instance {instid}..")
    instance = _getinstance(instid)
    version_id = instance.getmeta()["version"]
    if version_id not in versions:
        logger.error(f"Requested LSBQ-RML version '{version_id}' not found.")
        return {}
    buf: dict[str, dict[str, Any]] = {}
    for section in sections:
        if section in versions[version_id]:
            buf[section] = versions[version_id][section]
    return buf


@_expose
def init(data: dict[str, Any]) -> str:
    """Initialises a new LSBQ-RML Response."""
    logger.info("Creating new LSBQ-RML instance..")
    logger.debug(f"... received data: {data!r}")
    instance = Response()
    instid = instance.getid()
    logger.debug(f"... 'id' of instance is {instid}")
    instance.setmeta(
        {
            "version": data["selectSurveyVersion"],
            "researcher_id": data["researcherId"],
            "participant_id": data["participantId"],
            "research_location": data["researchLocation"],
            "consent": data["confirmConsent"],
            "date": datetime.date.today().isoformat(),
        }
    )
    instances[instid] = instance
    logger.info(f"... set 'meta' data to {instance.getmeta()}")
    booteel.setlocation(f"lsb.html?instance={instance.getid()}")
    return instid


@_expose
def setlsb(instid: str, data: dict[str, str]) -> str:  # noqa: C901
    """Adds Language and Social Background Data to a Response."""
    logger.info(f"Setting LSB data on LSBQ-RML instance {instid}..")
    logger.debug(f"... received data: {data!r}")
    instance = _getinstance(instid)
    processed: dict[str, Union[str, list[str]]] = {}
    processed["residencies_location"] = []
    processed["residencies_start"] = []
    processed["residencies_end"] = []
    datacopy = copy(data)
    for key in datacopy:
        if "otherPlacesName-" in key:
            index = key[16:]
            location_key = f"otherPlacesName-{index}"
            start_key = f"otherPlacesFrom-{index}"
            end_key = f"otherPlacesTo-{index}"
            if location_key in datacopy:
                location = datacopy[location_key]
                del data[location_key]
            else:
                location = ""
            if start_key in datacopy:
                start = datacopy[start_key]
                del data[start_key]
            else:
                start = ""
            if end_key in datacopy:
                end = datacopy[end_key]
                del data[end_key]
            else:
                end = ""
            if location + start + end != "":
                processed["residencies_location"].append(location)
                processed["residencies_start"].append(start)
                processed["residencies_end"].append(end)
        if datacopy[key] is None:
            print("!!!\nFIELD WITH KEY", key, "IS None\n!!!")
            del data[key]
    processed.update(data)
    logger.debug(f"... preprocessed data: {processed!r}")
    instance.setlsb(processed)
    logger.info(f"... set 'lsb' data to {instance.getlsb()}")
    booteel.setlocation(f"ldb.html?instance={instance.getid()}")
    return instid


@_expose
def setldb(instid: str, data: dict[str, Any]) -> str:  # noqa: C901
    """Adds Language and Dialect Background Data to a Response."""
    logger.info(f"Setting LDB data on LSBQ-RML instance {instid}..")
    logger.debug(f"... received data: {data!r}")
    instance = _getinstance(instid)
    processed: dict[str, Union[str, int, list[Union[str, int]]]] = {
        "languages_spoken_name": [],
        "languages_spoken_source": [],
        "languages_spoken_source_other": [],
        "languages_spoken_age": [],
        "languages_spoken_breaks": [],
        "languages_proficiency_speaking": [],
        "languages_proficiency_understanding": [],
        "languages_usage_speaking": [],
        "languages_usage_listening": [],
    }
    datacopy = copy(data)
    strip_keys = [
        "languageListOptions",
        "motherNotApplicable",
        "fatherNotApplicable",
    ]
    mother_keys = [
        "mother_occupation",
        "mother_first_language",
        "mother_second_language",
        "mother_other_languages",
    ]
    father_keys = [
        "father_occupation",
        "father_first_language",
        "father_second_language",
        "father_other_languages",
    ]
    if datacopy["motherNotApplicable"]:
        strip_keys.extend(mother_keys)
    if datacopy["fatherNotApplicable"]:
        strip_keys.extend(father_keys)
    for key in datacopy:
        if key in strip_keys:
            del data[key]
        if "languagesSpokenLanguage-" in key:
            append_row = True
            if datacopy[key].strip() == "":
                append_row = False
            index = key[24:]
            key_map = {
                f"languagesSpokenLanguage-{index}": "languages_spoken_name",
                f"languagesSpokenSource-{index}": "languages_spoken_source",
                f"languagesSpokenSourceSpecify-{index}": "languages_spoken_source_other",
                f"languagesSpokenAge-{index}": "languages_spoken_age",
                f"languagesSpokenBreakMonths-{index}": "languages_spoken_breaks",
                f"proficiencySpeakingLanguage-{index}": "languages_proficiency_speaking",
                f"proficiencyUnderstandingLanguage-{index}": "languages_proficiency_understanding",  # noqa: E501
                f"usageSpeakingLanguage-{index}": "languages_usage_speaking",
                f"usageListeningLanguage-{index}": "languages_usage_listening",
            }
            break_year_key = f"languagesSpokenBreakYears-{index}"
            source_specify_key = f"languagesSpokenSourceSpecify-{index}"
            for needle in key_map:
                fieldname = key_map[needle]
                if needle not in datacopy:
                    raise ValueError(
                        f"Data for {key!r} ({datacopy[key]!r}) "
                        f"is missing corresponding field {needle!r}"
                    )
                if "BreakMonths" in needle and break_year_key in datacopy:
                    datacopy[needle] = int(datacopy[needle])
                    datacopy[needle] += int(datacopy[break_year_key])*12
                    del data[break_year_key]
                if "languagesSpokenSource-" in needle and datacopy[needle].lower() != "o":
                    datacopy[source_specify_key] = 'n/a'
                if fieldname in processed and isinstance(processed[fieldname], list):
                    if append_row:
                        processed[fieldname].append(datacopy[needle])  # type: ignore
                    del data[needle]
                else:
                    raise RuntimeError(
                        f"Could not map {needle} to field {fieldname} (report as bug)"
                    )
    if "mother_second_language" in data and not data["mother_second_language"]:
        del data["mother_second_language"]
    if "father_second_language" in data and not data["father_second_language"]:
        del data["father_second_language"]
    processed.update(data)
    logger.debug(f"... preprocessed data: {processed!r}")
    instance.setldb(processed)
    logger.debug(f"LSBQ-RML instance id = {instid}")
    logger.debug(f"... set 'ldb' data to {instance.getldb()}")
    booteel.setlocation(f"club.html?instance={instance.getid()}")
    return instid


@_expose
def setclub(instid: str, data: dict[str, Any]) -> str:  # noqa: C901
    """Adds Community Language Use Behaviour Data to a Response."""
    logger.info(f"Setting CLUB data on LSBQ-RML instance {instid}..")
    logger.debug(f"... received data: {data!r}")
    instance = _getinstance(instid)

    camel_case_matcher = re.compile(r"([a-z])([A-Z])")

    def camel_to_snake_case(x: str) -> str:
        """Converts a string in camelCase."""
        return camel_case_matcher.sub(r"\1_\2", x).lower()

    data = {camel_to_snake_case(key): value for key, value in data.items()}

    def field_applicable(group: str, field: str):
        """Checks whether 'field' in 'group' is marked as not applicable."""
        return not (
            f"{group}_not_applicable-{field}" in data and
            data[f"{group}_not_applicable-{field}"]
        )

    processed: dict[str, Any] = {}
    for key, value in data.items():
        (group, field) = key.split("-", 2)
        if group == "life_stage":
            if not field.endswith("_age"):
                field += "_age"
            processed[field] = value
        elif group == "with_people_now" and field_applicable(group, field):
            processed[field] = value
        elif group == "with_people_early_life" and field_applicable(group, field):
            processed[f"childhood_{field}"] = value
        elif group == "situation" and field_applicable(group, field):
            processed[field] = value
        elif group == "activity" and field_applicable(group, field):
            processed[field] = value

    logger.debug(f"... preprocessed data: {processed!r}")
    instance.setclub(processed)

    logger.debug(f"LSBQ-RML instance id = {instid}")
    logger.debug(f"... set 'club' data to {instance.getclub()}")
    booteel.setlocation(f"end.html?instance={instance.getid()}")
    return instid


@_expose
def setnotes(instid: str, data: dict[str, Any]) -> str:
    """Adds Participant and Experimenter Comments Data to a Response."""
    logger.info(f"Setting Notes data on LSBQ-RML instance {instid}..")
    logger.debug(f"... received data: {data!r}")
    instance = _getinstance(instid)
    instance.setnotes({"participant_note": data["participantNote"]})
    logger.debug(f"LSBQ-RML instance id = {instid}")
    logger.debug(f"... set 'notes' data to {instance.getnotes()}")
    store(instid)
    meta = instance.getmeta()
    params = {
        "selectSurveyVersion": meta["version"],
        "researcherId": meta["researcher_id"],
        "researchLocation": meta["research_location"],
        "participantId": meta["participant_id"],
        "confirmConsent": int(meta["consent"]),
        "surveyDataForm.submit": "true",
    }
    query = "&".join(
        [f"{key}={urlquote(str(value), safe='')}" for key, value in params.items()]
    )
    booteel.setlocation(f"/app/atol-c/index.html?{query}")
    return instid


@_expose
def getversions() -> dict[str, str]:
    """Retrieves the available versions of the LSBQ RML."""
    # return {
    #     "CymEng_Eng_GB": "Welsh – English (United Kingdom)",
    #     "CymEng_Cym_GB": "Cymraeg – Saesneg (Deyrnas Unedig)",
    #     "LmoIta_Ita_IT": "Lombard – Italiano (Italia)",
    #     "LtzGer_Ger_BE": "Moselfränkisch – Deutsch (Belgien)",
    # }
    lsbq_versions: dict[str, str] = {}
    for identifier in versions.keys():
        lsbq_versions[identifier] = versions[identifier]["meta"]["versionName"]
    return lsbq_versions


@_expose
def iscomplete(instid: str) -> bool:
    """Checks whether a Response is complete."""
    instance = _getinstance(instid)
    completeness = instance.iscomplete()
    logger.debug(f"LSBQ-RML instance id = {instid}")
    logger.debug(f"... checking complete: {completeness}")
    return completeness


@_expose
def getmissing(instid: str) -> list[str]:
    """Gets a list of missing fields."""
    instance = _getinstance(instid)
    missing = instance.missing()
    logger.debug(f"LSBQ-RML instance id = {instid}")
    logger.debug(f"... checking missing fields: {missing}")
    return missing


@_expose
def discard(instid: str) -> bool:
    """Discards a Response."""
    if instid not in instances:
        raise AttributeError(f"No current response instance with instid `{instid}`.")
    del instances[instid]
    logger.debug(f"LSBQ-RML instance id = {instid}")
    logger.debug(f"... discarded instance with id {instid}")
    return True


@_expose
def store(instid: str) -> bool:
    """Submits a (complete) Response for long-term storage."""
    logger.info(f"Storing data of LSBQ-RML instance {instid}..")
    instance = _getinstance(instid)
    d = instance.data()
    s = json.dumps(d, indent=4)
    logger.info(f"... JSON serialization: {s}")
    path: Path = config.paths.data / "LSBQ-RML" / d["meta"]["version"]
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    filename = path / (str(instid) + ".json")
    logger.info(f"... writing to filename: {filename}")
    with filename.open("w") as fp:
        fp.write(s)
    logger.debug("... file saved successfully.")
    return True
