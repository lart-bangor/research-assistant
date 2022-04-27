"""Exposes the Memory Game to Python Eel."""
import datetime
import eel
import logging
import json
from functools import wraps
from pathlib import Path
from typing import Optional, Union, Callable, Any, TypeVar, cast
from .. import booteel
from ..config import config
from ..datavalidator.exceptions import DataValidationError
from .dataschema import Response
from .versions import versions

logger = logging.getLogger(__name__)

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
    eel._expose("_memorygame_" + func.__name__, api_wrapper)  # type: ignore
    return cast(F, api_wrapper)


@_expose
def load_version(instid: str, sections: list[str]) -> dict[str, dict[str, Any]]:
    """Load specified sections of a Memory Game version implementation."""
    logger.info(f"Retrieving version data for Memory Game instance {instid}..")
    instance = _getinstance(instid)
    version_id = instance.getmeta()["version"]
    if version_id not in versions:
        logger.error(f"Requested Memory Game version '{version_id}' not found.")
        return {}
    buf: dict[str, dict[str, Any]] = {}
    for section in sections:
        if section in versions[version_id]:
            buf[section] = versions[version_id][section]
    return buf


@_expose
def init(data: dict[str, Any]) -> str:
    """Initialises a new Memory Game Response."""
    logger.info("Creating new Memory Game instance..")
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
    booteel.setlocation(f"game.html?instance={instance.getid()}")
    return instid


@_expose
def setscores(instid: str, data: dict[str, str]) -> str:  # noqa: C901
    """Adds Memory Game Scores to a Response."""
    logger.info(f"Setting scores on Memory Game instance {instid}..")
    logger.debug(f"... received data: {data!r}")
    instance = _getinstance(instid)
    instance.setscores(data)
    logger.info(f"... set 'scores' data to {instance.getscores()}")
    store(instid)
    booteel.setlocation(f"end.html?instance={instance.getid()}")
    return instid


@_expose
def getversions() -> dict[str, str]:
    """Retrieves the available versions of the Memory Game."""
    game_versions: dict[str, str] = {}
    for identifier in versions.keys():
        game_versions[identifier] = versions[identifier]["meta"]["versionName"]
    return game_versions


@_expose
def iscomplete(instid: str) -> bool:
    """Checks whether a Response is complete."""
    instance = _getinstance(instid)
    completeness = instance.iscomplete()
    logger.debug(f"Memory Game instance id = {instid}")
    logger.debug(f"... checking complete: {completeness}")
    return completeness


@_expose
def getmissing(instid: str) -> list[str]:
    """Gets a list of missing fields."""
    instance = _getinstance(instid)
    missing = instance.missing()
    logger.debug(f"Memory Game instance id = {instid}")
    logger.debug(f"... checking missing fields: {missing}")
    return missing


@_expose
def discard(instid: str) -> bool:
    """Discards a Response."""
    if instid not in instances:
        raise AttributeError(f"No current response instance with instid `{instid}`.")
    del instances[instid]
    logger.debug(f"Memory Game instance id = {instid}")
    logger.debug(f"... discarded instance with id {instid}")
    return True


@_expose
def store(instid: str) -> bool:
    """Submits a (complete) Response for long-term storage."""
    logger.info(f"Storing data of Memory Game instance {instid}..")
    instance = _getinstance(instid)
    d = instance.data()
    s = json.dumps(d, indent=4)
    logger.info(f"... JSON serialization: {s}")
    path: Path = config.paths.data / "Memory-Game" / d["meta"]["version"]
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    filename = path / f"{d['meta']['participant_id']}_{instid}.json"
    logger.info(f"... writing to filename: {filename}")
    with filename.open("w") as fp:
        fp.write(s)
    logger.debug("... file saved successfully.")
    return True
