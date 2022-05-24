"""Exposes app configuration to Python Eel as Settings."""
import eel
import logging
from functools import wraps
from typing import Optional, Union, Callable, Any, TypeVar, cast
from .. import booteel
from ..config import config
from ..datavalidator.exceptions import DataValidationError
# from .dataschema import Response

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
    eel._expose("_settings_" + func.__name__, api_wrapper)  # type: ignore
    return cast(F, api_wrapper)


@_expose
def load() -> dict[str, dict[str, Any]]:
    """Return current settings and config documentation."""
    logger.info("Fetching app settings..")
    dataclasses, fields = config.getdocs()
    settings: dict[str, dict[str, Any]] = {}
    # Add general settings fields
    settings["root"] = {
        "name": "root",
        "label": "General",
        "help": "General app settings.",
        "fields": fields,
    }
    # Add sub-configuration sections
    for dataclass in dataclasses:
        settings[dataclass["name"]] = dataclass
        # Remove irrelevant/redundant attributes
        del settings[dataclass["name"]]["value"]
        del settings[dataclass["name"]]["type"]
        del settings[dataclass["name"]]["default"]
        # Remove sub-dataclasses from fields attribute
        settings[dataclass["name"]]["fields"] = settings[dataclass["name"]]["fields"][1]
    logger.debug(f"    Settings: {settings}")
    return settings


@_expose
def store(settings: dict[str, dict[str, Any]]) -> bool:
    """Validate settings, store in config, and save.."""
    raise NotImplementedError
    return False
