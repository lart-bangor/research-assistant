"""Exposes the Conclusion screen to Python Eel."""
import eel
import logging
from functools import wraps
from typing import Optional, Union, Callable, Any, TypeVar, cast
from .. import booteel
from ..config import config
from .versions import versions

logger = logging.getLogger(__name__)

# TypeVar for function wrappers
F = TypeVar("F", bound=Callable[..., Any])

# Function to be called to handle exceptions, or None to not handle exceptions
exceptionhandler: Optional[Callable[..., None]] = None


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
            booteel.displayexception(exc)
            _handleexception(exc)
            return False
    eel._expose("_conclusion_" + func.__name__, api_wrapper)  # type: ignore
    return cast(F, api_wrapper)


@_expose
def getversions() -> dict[str, str]:
    """Retrieves the available versions of the Conclusion screen."""
    conclusion_versions: dict[str, str] = {}
    for identifier in versions.keys():
        conclusion_versions[identifier] = versions[identifier]["meta"]["versionName"]
    return conclusion_versions


@_expose
def load_version(version_id: str, sections: list[str]) -> dict[str, dict[str, Any]]:
    """Load specified sections of a Conclusion screen version implementation."""
    logger.info(f"Retrieving version data for Conclusion screen version {version_id}..")
    if version_id not in versions:
        logger.error(f"Requested Conclusion screen version '{version_id}' not found.")
        return {}
    buf: dict[str, dict[str, Any]] = {}
    for section in sections:
        if section in versions[version_id]:
            buf[section] = versions[version_id][section]
    return buf


@_expose
def init(data: dict[str, Any]) -> str:
    """Initialises a new Conclusion screen instance."""
    logger.info("Creating new Conclusion screen instance..")
    logger.debug(f"... received data: {data!r}")
    version_id = data["selectSurveyVersion"]
    if version_id not in versions:
        logger.error(f"Requested Conclusion screen version '{version_id}' not found.")
    logger.info(f"... set 'version' to {version_id}")
    booteel.setlocation(f"end.html?versionId={version_id}")
    return version_id


@_expose
def end(version_id: str) -> bool:
    """Redirect following sequence logic after conclusion screen ends."""
    logger.info(f"Redirecting after conclusion screen..")
    if config.sequences.conclusion:
        query = booteel.buildquery({
            "selectSurveyVersion": version_id,
            "surveyDataForm.submit": "true",
        })
        booteel.setlocation(f"/app/{config.sequences.conclusion}/index.html?{query}")
    else:
        booteel.setlocation("/app/index.html")
    return True
