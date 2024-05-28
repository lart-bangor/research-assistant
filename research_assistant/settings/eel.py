"""Exposes app configuration / settings to Python Eel."""

import logging
from dataclasses import is_dataclass
from pathlib import Path
from typing import Any

import eel

from ..booteel import utils as booteel_utils
from ..booteel.eel_api import EelAPI
from ..booteel.errors import InvalidValueError
from ..config import config

logger = logging.getLogger(__name__)


class SettingsAPI(EelAPI):
    """Exposable API to load and store app settings."""

    eel_namespace: str = "settings"
    logger = logger

    @classmethod
    def exception_handler(cls, exc: Exception) -> None:
        """Exception handler for exceptions occuring during `SettingsAPI` calls.

        Handles exceptions by logging them and passing them to the frontend
        via booteel.

        Arguments:
            exc: The exception that needs to be handled.
        """
        booteel_utils.displayexception(exc)
        cls.logger.exception(exc)

    @EelAPI.exposed
    def load(self) -> dict[str, dict[str, Any]]:    # noqa: C901
        """Return current settings and config documentation."""
        self.logger.info("Fetching app settings..")
        dataclasses, fields = config.getdocs()
        settings: dict[str, dict[str, Any]] = dict()
        # Add general settings fields
        settings["root"] = {
            "name": "root",
            "label": "General",
            "help": "General app settings.",
            "fields": fields,
        }
        for dataclass in dataclasses:
            settings[dataclass["name"]] = dataclass
            # Remove irrelevant/redundant attributes
            for key in ("value", "type", "default"):
                if key in settings[dataclass["name"]]:
                    del settings[dataclass["name"]][key]
            # Remove sub-dataclasses from fields attribute
            settings[dataclass["name"]]["fields"] = settings[dataclass["name"]][
                "fields"
            ][1]
            # For Path type arguments, convert default and value to string
            for fieldindex in range(0, len(settings[dataclass["name"]]["fields"])):
                if isinstance(
                    settings[dataclass["name"]]["fields"][fieldindex]["default"], Path
                ):
                    settings[dataclass["name"]]["fields"][fieldindex]["default"] = str(
                        settings[dataclass["name"]]["fields"][fieldindex]["default"]
                    )
                if isinstance(
                    settings[dataclass["name"]]["fields"][fieldindex]["value"], Path
                ):
                    settings[dataclass["name"]]["fields"][fieldindex]["value"] = str(
                        settings[dataclass["name"]]["fields"][fieldindex]["value"]
                    )
        logger.debug(f"    settings: {settings}")
        return settings

    @EelAPI.exposed
    def store(self, settings: dict[str, dict[str, Any]]) -> bool:  # noqa: C901
        """Validate settings, store in config, and save."""
        self.logger.info("Storing updated app settings..")
        self.logger.debug(f"  .. current config: {config.asdict()}")
        self.logger.debug(f"  .. data received: {settings}")
        for key, value in settings.items():
            if not key.startswith("settings-"):
                continue
            key = key.removeprefix("settings-")
            if "-" not in key:
                continue
            section, property = key.split("-", maxsplit=1)
            target = None
            if section == "root":
                target = config
            elif hasattr(config, section) and is_dataclass(getattr(config, section)):
                target = getattr(config, section)
            if target is None or not hasattr(target, property):
                continue
            self.logger.debug(f"  .. setting {property} on {target} to {value!r}")
            target_type = type(getattr(target, property))
            if type(value) is not target_type:
                debug_msg = f"  .. value is of type {type(value)}; coercion to {target_type} {{}}."
                try:
                    value = target_type(value)
                    self.logger.debug(debug_msg.format("succeeded"))
                except ValueError:
                    self.logger.debug(debug_msg.format("failed"))
                    raise InvalidValueError(
                        (
                            f"Could not cast value {value!r} of type {type(value)} to {target_type}"
                            f" for field config.{section}.{property}"
                        ),
                        task=self.eel_namespace,
                    )
            setattr(target, property, value)
        config.save()
        logger.info("  .. settings stored successfully.")
        logger.debug(f"  .. new config data as stored: {config.asdict()}")
        eel._settings_notify_successful_update()  # type: ignore
        return True


# Required so importers know which class defines the API
eel_api = SettingsAPI
