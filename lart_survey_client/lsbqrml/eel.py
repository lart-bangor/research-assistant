"""Exposes the LSBQ-RML to Python Eel."""
import eel
from typing import Optional, Union, Callable, Any, TypeVar, cast
from functools import wraps
from lsbqrml import Response, logger
import datetime
from copy import copy
from datavalidator.exceptions import DataValidationError
import booteel

# TypeVar for function wrappers
F = TypeVar("F", bound=Callable[..., Any])

# Function to be called to handle exceptions, or None to not handle exceptions
exceptionhandler: Optional[Callable[..., None]] = None

# Keeps track of current Response instances
instances: dict[int, Response] = {}


def _getinstance(instid: Union[int, str]) -> Response:
    if not isinstance(instid, int):
        instid = int(instid)
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
def init(data: dict[str, Any]) -> int:
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
def setlsb(instid: int, data: dict[str, str]) -> int:
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
def setldb(instid: int, data: dict[str, Any]) -> int:
    """Adds Language and Dialect Background Data to a Response."""
    logger.info(f"Setting LDB data on LSBQ-RML instance {instid}..")
    logger.debug(f"... received data: {data!r}")
    from pprint import pp
    print(f"Setting LDB data on LSBQ-RML instance {instid}..")
    print("... received data:")
    pp(data)
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
                    processed[fieldname].append(datacopy[needle])  # type: ignore
                    del data[needle]
                else:
                    raise RuntimeError(
                        f"Could not map {needle} to field {fieldname} (report as bug)"
                    )
    processed.update(data)
    print("... preprocessed data:")
    pp(processed)
    logger.debug(f"... preprocessed data: {processed!r}")
    instance.setldb(processed)
    logger.debug(f"LSBQ-RML instance id = {instid}")
    logger.debug(f"... set 'ldb' data to {instance.getldb()}")
    booteel.setlocation(f"club.html?instance={instance.getid()}")
    return instid


@_expose
def setclub(instid: int, data: dict[Any, Any]) -> int:
    """Adds Community Language Use Behaviour Data to a Response."""
    instance = _getinstance(instid)
    instance.setclub(

    )
    logger.debug(f"LSBQ-RML instance id = {instid}")
    logger.debug(f"... set 'club' data to {instance.getclub()}")
    booteel.setlocation(f"notes.html?instance={instance.getid()}")
    return instid


@_expose
def setnotes(instid: int, data: dict[Any, Any]) -> int:
    """Adds Participant and Experimenter Comments Data to a Response."""
    instance = _getinstance(instid)
    instance.setnotes(

    )
    logger.debug(f"LSBQ-RML instance id = {instid}")
    logger.debug(f"... set 'notes' data to {instance.getnotes()}")
    booteel.setlocation(f"finish.html?instance={instance.getid()}")
    return instid


@_expose
def getversions() -> dict[str, str]:
    """Retrieves the available versions of the LSBQ RML."""
    return {
        "CymEng_Eng_GB": "Welsh – English (United Kingdom)",
        "CymEng_Cym_GB": "Cymraeg – Saesneg (Deyrnas Unedig)",
        "LmoIta_Ita_IT": "Lombard – Italiano (Italia)",
        "LtzGer_Ger_BE": "Moselfränkisch – Deutsch (Belgien)",
    }


@_expose
def iscomplete(instid: int) -> bool:
    """Checks whether a Response is complete."""
    instance = _getinstance(instid)
    completeness = instance.iscomplete()
    logger.debug(f"LSBQ-RML instance id = {instid}")
    logger.debug(f"... checking complete: {completeness}")
    return completeness


@_expose
def getmissing(instid: int) -> list[str]:
    """Gets a list of missing fields."""
    instance = _getinstance(instid)
    missing = instance.missing()
    logger.debug(f"LSBQ-RML instance id = {instid}")
    logger.debug(f"... checking missing fields: {missing}")
    return missing


@_expose
def discard(instid: int) -> bool:
    """Discards a Response."""
    if instid not in instances:
        raise AttributeError(f"No current response instance with instid `{instid}`.")
    del instances[instid]
    logger.debug(f"LSBQ-RML instance id = {instid}")
    logger.debug(f"... discarded instance with id {instid}")
    return True


@_expose
def store(instid: int) -> bool:
    """Submits a (complete) Response for long-term storage."""
    instance = _getinstance(instid)
    logger.debug(f"LSBQ-RML instance id = {instid}")
    logger.debug(f"... asking to store instance {instance}")
    logger.debug("... ERROR: storage not implemented yet!")
    raise NotImplementedError()
    return True
