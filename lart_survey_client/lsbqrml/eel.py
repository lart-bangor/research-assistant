"""Exposes the LSBQ-RML to Python Eel."""
import eel
from typing import Optional, Union, Callable, Any, TypeVar, cast
from functools import wraps
from lsbqrml import Response


# TypeVar for function wrappers
F = TypeVar("F", bound=Callable[..., Any])

# Function to be called to handle exceptions, or None to not handle exceptions
exceptionhandler: Optional[Callable[..., None]] = None

# Keeps track of current Response instances
instances: dict[str, Response] = {}


def _handleexception(exc: Exception) -> None:
    """Passes exception to exceptionhandler if defined, otherwise continues raising."""
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
            _handleexception(exc)
            return False
    eel._expose("_lsbqrml_" + func.__name__, api_wrapper)  # type: ignore
    return cast(F, api_wrapper)


@_expose
def init(data: dict[Any, Any]) -> str:
    """Initialises a new LSBQ-RML Response."""
    instance = Response()
    instance.setmeta(
        data["selectSurveyVersion"],
        data["researcherId"],
        data["researchLocation"],
        data["participantId"],
        data["confirmConsent"]
    )
    instid = instance.getid()
    instances[instid] = instance
    return instid


@_expose
def setlsb(instid: str, data: dict[Any, Any]) -> bool:
    """Adds Language and Social Background Data to a Response."""
    if instid not in instances:
        raise AttributeError(f"No current response instance with instid `{instid}`.")
    instance = instances[instid]
    instance.setlsb(
        data["sex"],
        data["sexOther"],
        data["occupation"],
        data["handedness"],
        data["dateOfBirth"],
        data["hearingImpairment"],
        data["hearingAid"],
        data["visionImpairment"],
        data["visionAid"],
        data["visionFullyCorrected"],
        data["placeOfBirth"],
        data["placesOfSignificantResidence"],
        data["educationLevel"]
    )
    return True


@_expose
def setldb(instid: str, data: dict[Any, Any]) -> bool:
    """Adds Language and Dialect Background Data to a Response."""
    raise NotImplementedError()
    return False


@_expose
def setclub(instid: str, data: dict[Any, Any]) -> bool:
    """Adds Community Language Use Behaviour Data to a Response."""
    raise NotImplementedError()
    return False


@_expose
def setcomments(instid: str, data: dict[Any, Any]) -> bool:
    """Adds Participant and Experimenter Comments Data to a Response."""
    raise NotImplementedError()
    return False


@_expose
def getversions() -> dict[str, str]:
    """Retrieves the available versions of the LSBQ RML."""
    raise NotImplementedError()
    return {}


@_expose
def iscomplete() -> bool:
    """Checks whether a Response is complete."""
    raise NotImplementedError()
    return False


@_expose
def getmissing() -> list[str]:
    """Gets a list of missing fields."""
    raise NotImplementedError()
    return False


@_expose
def discard() -> bool:
    """Discards a Response."""
    raise NotImplementedError()
    return False


@_expose
def store() -> bool:
    """Submits a (complete) Response for long-term storage."""
    raise NotImplementedError()
    return False
