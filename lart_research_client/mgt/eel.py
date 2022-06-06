"""Exposes the LSBQ-RML to Python Eel."""
import logging
import datetime
import eel
import json
from functools import wraps
from pathlib import Path
from random import sample
from typing import Optional, Union, Callable, Any, TypeVar, cast
from .dataschema import Response, mgt_traits, mgt_trials
from .versions import versions
from .. import booteel
from ..config import config
from ..datavalidator.exceptions import DataValidationError

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


def _getnexttrial(instid: str, current_trial: str) -> str | None:
    """Return the trial following *current_trial* on an MGT Response."""
    instance = _getinstance(instid)
    trials: list[str] = instance.gettrial_order()
    if current_trial not in trials:
        raise ValueError(f"Trial id {current_trial!r} is unknown.")
    next_index = trials.index(current_trial) + 1
    if next_index < len(trials):
        logger.info(f"Next MGT trial: {trials[next_index]}")
        return trials[next_index]
    logger.warning("No further MGT trials in list")
    return None


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
    eel._expose("_mgt_" + func.__name__, api_wrapper)  # type: ignore
    return cast(F, api_wrapper)


@_expose
def load_version(instid: str, sections: list[str]) -> dict[str, dict[str, Any]]:
    """Load specified sections of an MGT version implementation."""
    logger.info(f"Retrieving version data for MGT instance {instid}..")
    instance = _getinstance(instid)
    version_id = instance.getmeta()["version"]
    if version_id not in versions:
        logger.error(f"Requested MGT version '{version_id}' not found.")
        return {}
    buf: dict[str, dict[str, Any]] = {}
    for section in sections:
        if section in versions[version_id]:
            buf[section] = versions[version_id][section]
    return buf


@_expose
def get_traits():
    """Return the list of MGT stimuli."""
    return sample(mgt_traits, k=len(mgt_traits))


@_expose
def init(data: dict[str, Any]) -> str:
    """Initialises a new MGT Response."""
    logger.info("Creating new MGT instance..")
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
    trial_order: tuple[str, ...] = ("practice", ) + instance.generate_trial_order()
    logger.info(f"... setting trial order: {trial_order}.")
    instance.settrial_order(trial_order)                                        # type: ignore
    instances[instid] = instance
    logger.info(f"... set 'meta' data to {instance.getmeta()}")
    booteel.setlocation(f"instructions.html?instance={instance.getid()}")
    return instid


@_expose
def setratings(instid: str, data: dict[str, str]) -> None:
    """Adds the ratings for a given trial and redirects to the next trial."""
    logger.info(f"Setting trial ratings on MGT instance {instid}...")
    logger.debug(f"... received data: {data!r}")
    instance = _getinstance(instid)
    if "trial" not in data:
        raise ValueError("Missing trial id.")
    if data["trial"] not in mgt_trials:
        raise ValueError(f"Unknown trial id {data['trial']!r}")
    trait_ratings: dict[str, float] = {}
    for key in data:
        if key.startswith("trait-"):
            trait_ratings[key.removeprefix("trait-")] = float(data[key])
    logger.debug(f"... preprocessed data: {trait_ratings!r}")
    instance.setratings(data["trial"], trait_ratings)
    logger.info(f"... set {data['trial']!r} data to {instance.getratings(data['trial'])}")
    next_trial = _getnexttrial(instid, data["trial"])
    if next_trial is None:
        store(instance.getid())
        booteel.setlocation(f"end.html?instance={instance.getid()}")
    else:
        booteel.setlocation(f"rating.html?instance={instance.getid()}&trial={next_trial}")


@_expose
def getversions() -> dict[str, str]:
    """Retrieves the available versions of the MGT."""
    mgt_versions: dict[str, str] = {}
    for identifier in versions.keys():
        mgt_versions[identifier] = versions[identifier]["meta"]["versionName"]
    return mgt_versions


@_expose
def iscomplete(instid: str) -> bool:
    """Checks whether a Response is complete."""
    instance = _getinstance(instid)
    completeness = instance.iscomplete()
    logger.debug(f"MGT instance id = {instid}")
    logger.debug(f"... checking complete: {completeness}")
    return completeness


@_expose
def getmissing(instid: str) -> list[str]:
    """Gets a list of missing fields."""
    instance = _getinstance(instid)
    missing = instance.missing()
    logger.debug(f"MGT instance id = {instid}")
    logger.debug(f"... checking missing fields: {missing}")
    return missing


@_expose
def discard(instid: str) -> bool:
    """Discards a Response."""
    if instid not in instances:
        raise AttributeError(f"No current response instance with instid `{instid}`.")
    del instances[instid]
    logger.debug(f"MGT instance id = {instid}")
    logger.debug(f"... discarded instance with id {instid}")
    return True


@_expose
def store(instid: str) -> bool:
    """Submits a (complete) Response for long-term storage."""
    logger.info(f"Storing data of MGT instance {instid}..")
    instance = _getinstance(instid)
    d = instance.data()
    s = json.dumps(d, indent=4)
    logger.info(f"... JSON serialization: {s}")
    path: Path = config.paths.data / "MGT" / d["meta"]["version"]
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    participant_id = d["meta"]["participant_id"]
    filename = path / f"{participant_id}_{instid}.json"
    logger.info(f"... writing to filename: {filename}")
    with filename.open("w") as fp:
        fp.write(s)
    logger.debug("... file saved successfully.")
    return True
