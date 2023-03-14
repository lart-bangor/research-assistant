"""Exposes app configuration to Python Eel as Settings."""
import eel
import logging
from dataclasses import is_dataclass
from functools import wraps
from pathlib import Path
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
        # For Path type arguments, convert default and value to string
        for fieldindex in range(0, len(settings[dataclass["name"]]["fields"])):
            if isinstance(settings[dataclass["name"]]["fields"][fieldindex]["default"], Path):
                settings[dataclass["name"]]["fields"][fieldindex]["default"] = str(settings[dataclass["name"]]["fields"][fieldindex]["default"])
            if isinstance(settings[dataclass["name"]]["fields"][fieldindex]["value"], Path):
                settings[dataclass["name"]]["fields"][fieldindex]["value"] = str(settings[dataclass["name"]]["fields"][fieldindex]["value"])
    logger.debug(f"    Settings: {settings}")
    return settings


@_expose
def store(settings: dict[str, dict[str, Any]]) -> bool:                         # noqa: C901
    """Validate settings, store in config, and save.."""
    from pprint import pprint
    pprint(config.asdict())
    logger.info("Updating app settings...")
    logger.debug(f"Data received: {settings}")
    for key, value in settings.items():
        if not key.startswith("settings-"):
            continue
        key = key.removeprefix("settings-")
        if "-" not in key:
            continue
        section, property = key.split("-")
        target = None
        if section == "root":
            target = config
        elif hasattr(config, section) and is_dataclass(getattr(config, section)):
            target = getattr(config, section)
        if target is None:
            continue
        if hasattr(target, property):
            print(f"Setting {property} on {target}")
            target_type = type(getattr(target, property))
            if type(value) is not target_type:
                print(f"VALUE IS TYPE {type(value)} - target is type {target_type}")
                try:
                    value = target_type(value)
                    print("CONVERSION SUCCESSFUL:", value)
                except ValueError:
                    print("CONVERSION NOT SUCCESSFUL :->")
                    raise ValueError(
                        f"Could not convert input {value!r} to required type {target_type} "
                        f"for field config.{section}.{property}"
                    )
            setattr(target, property, value)
    config.save()
    logger.info(f"Settings successfully updated to {config.asdict()}.")
    pprint(config.asdict())
    eel._settings_notify_successful_update()                                    # type: ignore
    return True
