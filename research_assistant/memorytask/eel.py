"""Exposes the Memory Task to Python Eel."""
import eel
import logging
from functools import wraps
from pathlib import Path
from typing import Optional, Union, Callable, Any, TypeVar, cast
from .. import booteel
from ..config import config
from pydantic import ValidationError
from ..datamodels.models import ResponseMetadata
from ..datamodels.utils import validation_error_to_html
from .datamodel import MemoryTaskResponse, MemoryTaskScore
from .versions import versions as localisations
from uuid import UUID

logger = logging.getLogger(__name__)

# TypeVar for function wrappers
F = TypeVar("F", bound=Callable[..., Any])

# Function to be called to handle exceptions, or None to not handle exceptions
exceptionhandler: Optional[Callable[..., None]] = None

# Keeps track of current Response instances
instances: dict[UUID, MemoryTaskResponse] = {}


def _getinstance(instid: str | UUID) -> MemoryTaskResponse:
    if not isinstance(instid, UUID):
        instid = UUID(instid)
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
            if isinstance(exc, ValidationError):
                booteel.modal(
                    "Data Validation Error",
                    validation_error_to_html(exc)
                )
                _handleexception(exc)
            else:
                booteel.displayexception(exc)
                _handleexception(exc)
            return False
    eel._expose("_memorytask_" + func.__name__, api_wrapper)  # type: ignore
    return cast(F, api_wrapper)


@_expose
def load_version(instid: str | UUID, sections: list[str]) -> dict[str, dict[str, Any]]:
    """Load specified sections of a Memory Task localisation implementation."""
    if not isinstance(instid, UUID):
        instid = UUID(instid)
    logger.info(f"Retrieving localisation data for Memory Task instance {instid}..")
    instance = _getinstance(instid)
    task_localisation = instance.meta.task_localisation
    if task_localisation not in localisations:
        logger.error(f"Requested Memory Task localisation '{task_localisation}' not found.")
        return {}
    buf: dict[str, dict[str, Any]] = {}
    for section in sections:
        if section in localisations[task_localisation]:
            buf[section] = localisations[task_localisation][section]
    return buf


@_expose
def init(data: dict[str, Any]) -> str:
    """Initialises a new Memory Task Response."""
    logger.info("Creating new Memory Task instance..")
    logger.debug(f"... received data: {data!r}")
    task_localisation = data["selectSurveyVersion"]
    if task_localisation not in localisations:
        logger.error(f"Requested Memory Task localisation '{task_localisation}' not found.")
    metadata = ResponseMetadata(
        task_localisation=task_localisation,
        task_version_no=localisations[task_localisation]["meta"]["versionNumber"],
        app_version_no=config.appversion,
        app_system_useragent="Unknown",
        app_display_language="en_GB",
        researcher_id=data["researcherId"],
        research_location=data["researchLocation"],
        participant_id=data["participantId"],
        consent_obtained=data["confirmConsent"]
    )
    instance = MemoryTaskResponse(meta=metadata, scores=[])
    instid = instance.id
    instances[instid] = instance
    logger.debug(f"... 'id' of instance is {instid}")
    logger.info(f"... set 'meta' data to {instance.meta.dict()}")
    booteel.setlocation(f"game.html?instance={instance.id}")
    return instid


@_expose
def setscores(instid: str | UUID, data: dict[str, str]) -> str:  # noqa: C901
    """Adds Memory scores to a Memory Task Response."""
    if not isinstance(instid, UUID):
        instid = UUID(instid)
    logger.info(f"Setting scores on Memory Task instance {instid}..")
    logger.debug(f"... received data: {data!r}")
    instance = _getinstance(instid)
    for s, t in zip(data["score"], data["time"]):
        score = MemoryTaskScore(score=s, time=t)
        instance.scores.append(score)
    logger.info(f"... set 'scores' data to {instance.scores}")
    store(instid)
    booteel.setlocation(f"end.html?instance={instance.id}")
    return instid


@_expose
def getversions() -> dict[str, str]:
    """Retrieves the available versions of the Memory Task."""
    task_localisations: dict[str, str] = {}
    for identifier in localisations.keys():
        task_localisations[identifier] = localisations[identifier]["meta"]["versionName"]
    return task_localisations


@_expose
def discard(instid: str | UUID) -> bool:
    """Discards a Response."""
    if not isinstance(instid, UUID):
        instid = UUID(instid)
    if instid not in instances:
        raise AttributeError(f"No current response instance with instid `{instid}`.")
    del instances[instid]
    logger.debug(f"Memory Task instance id = {instid} has been discarded.")
    return True


@_expose
def store(instid: str) -> bool:
    """Submits a (complete) Memory Task Response for long-term storage."""
    logger.info(f"Storing data of Memory Task instance {instid}..")
    instance = _getinstance(instid)
    s = instance.json(indent=4)
    logger.info(f"... JSON serialization: {s}")
    path: Path = config.paths.data / "Memory-Task" / str(instance.meta.task_localisation)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    filename = path / f"{instance.meta.participant_id}_{instid}.json"
    logger.info(f"... writing to filename: {filename}")
    with filename.open("w") as fp:
        fp.write(s)
    logger.debug("... file saved successfully.")
    return True


@_expose
def end(instid: str | UUID, data: Optional[dict[str, str]] = None) -> str:
    """Redirect participant in right sequence after Memory Task end screen."""
    if not isinstance(instid, UUID):
        instid = UUID(instid)
    logger.info(f"Redirecting participant after completing Memory Task instance {instid}..")
    instance = _getinstance(instid)
    if config.sequences.memorytask:
        query = booteel.buildquery({
            "selectSurveyVersion": str(instance.meta.task_localisation),
            "researcherId": str(instance.meta.researcher_id),
            "researchLocation": str(instance.meta.research_location),
            "participantId": (instance.meta.participant_id),
            "confirmConsent": str(int(instance.meta.consent_obtained)),
            "surveyDataForm.submit": "true",
        })
        booteel.setlocation(f"/app/{config.sequences.memorytask}/index.html?{query}")
    else:
        booteel.setlocation("/app/index.html")
    return instid
