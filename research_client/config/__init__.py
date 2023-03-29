"""Configuration handler for L'ART Research Client.

This package provides an API to read, modify, and store app configuration. The
configuration is stored in a JSON file and relevant paths (unless explicitly
specified) are determined based on the Operating System (using the `AppDirs`
package).

The configuration package only exposes the actual interface to the configuration,
which is done via the singleton `config` object, an instantiation of the `Config`
class.

To access and/or modify the configuration of the running app, you should import
only `config`. The other classes and objects in the package will not typically
be needed, perhaps with the exceptions of functions that deal with system updates
and the like (as for instance the functionality in the
`research_client.utils` module).

Example:
    Let's imagine you want to ensure that the *shutdown_delay* setting is always
    at least three seconds. The following example shows how you would load the
    current app configuration, check the current value, and if it is below the
    threshold increase it to `3.00` and then save the modified configuration
    (so that it will persist when the app is restarted)::

        from .config import config

        if config.shutdown_delay < 3.00:
            config.shutdown_delay = 3.00
            config.save()
"""
from __future__ import annotations
import json
import logging
from platformdirs import PlatformDirs
from copy import copy
from dataclasses import MISSING, dataclass, field, fields, asdict, is_dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Final, Callable, ClassVar, Optional, Union, get_type_hints

__all__ = ["config", "Config", "_default_paths"]

logger = logging.getLogger(__name__)

_appname: str = "Research Client"
_appauthor: str = "L’ART"
_safeappname: str = "Research_Client"
_safeappauthor: str = "LART"
_default_paths = PlatformDirs(_safeappname, _safeappauthor, roaming=True)


class JSONPathEncoder(json.JSONEncoder):
    """JSON Encoder capable of serialising pathlib Path objects."""

    def default(self, o: Any):
        """Encodes pathlib Path objects as strings, otherwise uses default JSONEncoder."""
        if isinstance(o, Path):
            return str(o)
        return json.JSONEncoder.default(self, o)


class DataclassDictMixin:
    """Mixin adding asdict() and fromdict() methods to a dataclass."""

    @classmethod
    def fromdict(cls, d: dict[str, Any], ignorefaults: bool = False):  # noqa: C901
        """Recursively converts a dictionary to a dataclass instance."""
        if not is_dataclass(cls):
            raise TypeError(f"Class {cls!r} is not a dataclass.")
        type_map: dict[str, Callable[..., Any]] = {}
        for name, type_ in get_type_hints(cls).items():
            if isinstance(type_, str):
                if not type_.isalnum():
                    raise RuntimeError(f"Unsafe type annotation {type_!r}.")
                type_ = eval(type_)
            type_map[name] = type_
        args: dict[str, Any] = {}
        for name, value in d.items():
            if name not in type_map:
                if ignorefaults:
                    logger.error(
                        f"Dataclass {cls!r} has no attribute {name!r} - {name!r} will be ignored."
                    )
                    continue
                else:
                    raise ValueError(f"Dataclass {cls!r} has no attribute {name!r}.")
            if is_dataclass(type_map[name]) and isinstance(d[name], dict):
                if hasattr(type_map[name], "fromdict"):
                    value = type_map[name].fromdict(d[name], ignorefaults)  # type: ignore
                else:
                    raise TypeError(
                        f"Dataclass {type_map[name]!r} has no method 'fromdict'."
                    )
            args[name] = value
        return cls(**args)  # type: ignore

    def asdict(self) -> dict[str, Any]:
        """Return a deep copy of the dataclass as a dictionary."""
        d: dict[str, Any] = {}
        for field_ in fields(self):
            if not field_.init:
                continue
            value: Any = getattr(self, field_.name)
            if is_dataclass(value):
                if hasattr(value, "asdict"):
                    d[field_.name] = value.asdict()
                else:
                    d[field_.name] = asdict(value)
            else:
                d[field_.name] = copy(value)
        return d


class DataclassDocMixin:
    """Mixin adding a getdocs() method to a dataclass.

    This enables adding additional documentation to dataclass fields using the
    field's *metadata* property. The following metadata properties are read by
    the DataclassDocMixin:

    * doc_label: A human-friendly label/short description of a field.
    * doc_help: A human-friendly explanation of what a field does / why it's there.
    * doc_values: A dictionary of label-value pairs, which can be used to give
      an indication of specific values the field can take and what they mean.
    """

    def getdocs(                                                                # noqa: C901
        self,
        /,
        recurse: bool = True,
        include_undocumented: bool = False
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """Return a dictionary with documentation for the dataclass's fields.

        Arguments:
            recurse: Whether to also fetch the field-docs for fields that are
                dataclasses.
            include_undocumented: Whether to include fields that do not have
                at least *doc_label* assigned in their metadata.

        Returns: A two-tuple, where the first member is a list of dataclass
            fields, the second member a list of non-dataclass fields. Each list
            contains a dictionary with information about the field.
        """
        dataclasses: list[dict[str, Any]] = []
        fields_: list[dict[str, Any]] = []
        for field_ in fields(self):
            field_doc = {
                "value": getattr(self, field_.name),
                "name": field_.name,
                "type": field_.type
            }
            if "doc_label" in field_.metadata or include_undocumented:
                field_doc["label"] = field_.metadata["doc_label"]
            else:
                continue
            if "doc_help" in field_.metadata:
                field_doc["help"] = field_.metadata["doc_help"]
            if "doc_values" in field_.metadata:
                field_doc["values"] = field_.metadata["doc_values"]
            if field_.default is not MISSING:
                field_doc["default"] = field_.default
            if is_dataclass(field_doc["value"]):
                if recurse and isinstance(field_doc["value"], DataclassDocMixin):
                    field_doc["fields"] = field_doc["value"].getdocs(
                        recurse=recurse,
                        include_undocumented=include_undocumented
                    )
                dataclasses.append(field_doc)
            else:
                fields_.append(field_doc)
        return (dataclasses, fields_)


@dataclass
class Paths(DataclassDictMixin, DataclassDocMixin):
    """Class for configuration of App paths."""

    config: Path = field(
        default=_default_paths.user_config_path,
        init=False,
        metadata={
            "doc_label": "Path for configuration files",
            "doc_help": (
                "Note that changes to the configuration file path have no effect "
                "and will automatically revert to the default path. The path "
                "shown here is primarily of informational value."
            )
        }
    )
    data: Path = field(
        default=_default_paths.user_data_path / "Data",
        metadata={
            "doc_label": "Path for data files",
            "doc_help": (
                "This is the path where data files (responses) from the app's "
                "tasks are stored."
            )
        }
    )
    logs: Path = field(
        default=_default_paths.user_log_path,
        metadata={
            "doc_label": "Path for log files",
            "doc_help": (
                "This is the path where the app stores log files, which may "
                "contain useful information for debugging and error reporting. "
            )
        }
    )
    cache: Path = field(
        default=_default_paths.user_cache_path,
        metadata={
            "doc_label": "Path for temporarily cached data and files",
            "doc_help": (
                "This is a path where the app may temporarily cache "
                "(store, modify, delete) various files during operation."
            )
        }
    )

    def __post_init__(self):
        """Post-init method that ensures paths are all pathlib Path objects."""
        for field_ in fields(self):
            if field_.type == Path.__name__ and not isinstance(
                getattr(self, field_.name), Path
            ):
                setattr(self, field_.name, Path(getattr(self, field_.name)))


@dataclass
class Logging(DataclassDictMixin, DataclassDocMixin):
    """Class for Logging configuration."""

    max_files: int = field(
        default=10,
        metadata={
            "doc_label": "Maximum number of log files to keep",
            "doc_help": (
                "Indicates the maximal number of log files kept. "
                "If more log files are present on app startup, "
                "the oldest log files are deleted."
            ),
        }
    )
    default_level: int = field(
        default=logging.WARNING,
        metadata={
            "doc_label": "Default log level",
            "doc_help": (
                "Specifies the default log level on app startup, used"
                " if no log level is specified with the --debug [LEVEL] "
                "command line option."
            ),
            "doc_values": {
                "Debug": 10,
                "Info": 20,
                "Warning": 30,
                "Error": 40,
                "Critical": 50.
            },
        }
    )
    stream_format: str = field(
        default="{levelname}:{name}: {message}",
        metadata={
            "doc_label": "Console log message format",
            "doc_help": "Format for log and error messages displayed on the console.",
        }
    )
    file_format: str = field(
        default="[{asctime} {levelname:<8} {name}] {message}",
        metadata={
            "doc_label": "File log message format",
            "doc_help": "Format for log and error messages in the log files.",
        }
    )

    def get_stream_handler(self, stream: Any = None) -> logging.StreamHandler[Any]:
        """Return a `logging.StreamHandler` object for logging."""
        sh = logging.StreamHandler(stream)
        sh.setFormatter(logging.Formatter(self.stream_format, style="{"))
        return sh

    def get_file_handler(
        self,
        name: str,
        path: Optional[Union[Path, str]] = None
    ) -> logging.FileHandler:
        """Return a `logging.FileHandler` object for logging."""
        if path is None:
            path = config.paths.logs
        elif isinstance(path, str):
            path = Path(path)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        if not path.is_dir():
            raise ValueError(f"The specified path '{path}' is not a valid directory name.")
        filepath = self._get_file_path(name, path)
        fh = logging.FileHandler(filepath, mode="w", delay=True)
        fh.setFormatter(logging.Formatter(self.file_format, style="{"))
        return fh

    def _get_file_path(self, name: str, path: Path) -> Path:
        """Determine log file path and clear old log files.

        Scans *path* for logfiles named after *name* (*name*_*.log). If there
        are more than *config.logging.max_files - 1*, removes the oldest until
        that value is reached, and returns a path to a new log file (without
        creating it yet).
        """
        files = sorted(path.glob(f"{name}_*.log"))
        if len(files) >= (self.max_files - 1):
            for i in range(len(files) - self.max_files - 1):
                files[i].unlink()
        return path / f"{name}_{datetime.now():%Y%m%dT%H%M%S_%f}.log"


@dataclass
class Sequences(DataclassDictMixin, DataclassDocMixin):
    """Class for app-task sequencing configuration."""

    _sequence_options: ClassVar[dict[str, str]] = {
        "App start screen": "",
        "AGT": "agt",
        "AToL-C": "atolc",
        "Conclusion Screen": "conclusion",
        "Consent Form": "consent",
        "LSBQe": "lsbq",
        "Memory Task": "memorygame",
    }
    agt: str = field(
        default="",
        metadata={
            "doc_label": "Task following the AGT",
            "doc_values": _sequence_options,
        }
    )
    atolc: str = field(
        default="memorygame",
        metadata={
            "doc_label": "Task following the AToL-C",
            "doc_values": _sequence_options,
        }
    )
    conclusion: str = field(
        default="",
        metadata={
            "doc_label": "Task following the Conclusion Screen",
            "doc_values": _sequence_options
        }
    )
    consent: str = field(
        default="lsbq",
        metadata={
            "doc_label": "Task following the Consent Form",
            "doc_values": _sequence_options,
        }
    )
    lsbq: str = field(
        default="atolc",
        metadata={
            "doc_label": "Task following the LSBQe",
            "doc_values": _sequence_options,
        }
    )
    memorygame: str = field(
        default="",
        metadata={
            "doc_label": "Task following the Memory Task",
            "doc_values": _sequence_options,
        }
    )


@dataclass
class Config(DataclassDictMixin, DataclassDocMixin):
    """Class for keeping track of App configuration data."""

    appname: str = field(default=_appname, init=False)
    appauthor: str = field(default=_appauthor, init=False)
    appversion: str = field(default="0.3.4", init=False)
    logging: Logging = field(
        default=Logging(),
        metadata={
            "doc_label": "Logging settings",
            "doc_help": (
                "Configures the app's debug and error logging."
                "\n"
                "Modifying the logging settings can be useful for diagnosing "
                "errors you encounter or when developing new tasks using the "
                "app. Be mindful that it is easy to get 'too much information' "
                "if the logging levels are set to report very high detail."
            )
        }
    )
    paths: Paths = field(
        default=Paths(),
        metadata={
            "doc_label": "Path and directory settings",
            "doc_help": (
                "Configures the paths used by the app for storing and reading "
                "various files, such as data, settings, and logs."
                "\n"
                "It is strongly recommended that you do not modify any of the "
                "app paths unless you are positively confident that you know "
                "what you are doing. Incorrect path information could lead to "
                "unstable behaviour and in the worst case even data loss."
                "\n"
                "If paths are modified it is best to always restart the app and "
                "fully test that everything is working as expected, including "
                "inspecting the stored data files after running a task."
            )
        }
    )
    sequences: Sequences = field(
        default=Sequences(),
        metadata={
            "doc_label": "Task sequencing",
            "doc_help": (
                "Configures the automatic sequencing of tasks."
                "\n"
                "If a task is "
                "assigned a follow-up task, the user will be automatically "
                "redirected to the follow-up task upon completion."
            )
        }
    )
    shutdown_delay: float = field(
        default=2.0,
        metadata={
            "doc_label": "Shutdown delay",
            "doc_help": (
                "The number of seconds to wait with shutting down the app's "
                "backend process after the last window has been closed.\n"
                "Increasing this number slightly can help if you are running "
                "on slow/underpowered hardware and experience crashes."
            )
        }
    )

    def save(self, filename: str = "settings.json"):
        """Save configuration to a file."""
        path = self.paths.config / filename
        if not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
        d = self.asdict()
        logging.debug(
            f"Saving configuration to file: '{path}' "
            f"with values {json.dumps(d, cls=JSONPathEncoder)}"
        )
        try:
            with path.open("w") as fp:
                json.dump(d, fp, indent=4, cls=JSONPathEncoder)
        except Exception as e:
            logging.error(e)
            raise

    @classmethod
    def load(cls, filename: str = "settings.json") -> Config:
        """Load configuration from a file or return default Config()."""
        path = _default_paths.user_config_path / filename
        if path.exists():
            try:
                with path.open("r") as fp:
                    d = json.load(fp)
                cfg = Config.fromdict(d, ignorefaults=True)
                logging.debug(
                    f"Successfully loaded config from file ('{path}') with "
                    f"values: {json.dumps(cfg.asdict(), cls=JSONPathEncoder)}"
                )
                return cfg
            except (IOError, json.JSONDecodeError) as e:
                logging.error(f"Failed to load config file: {e}.")
                return Config()
        logging.debug("No configuration file found. Issuing hard-coded default settings.")
        return Config()


config: Final[Config] = Config.load()
"""The default configuration object for the app.

This is an instance of `Config` loaded from the users' stored settings upon module
initialisation (if available), otherwise it is populated with (sensible) default values.

When saved with `config.save()` it will automatically save in the correct file and
location depending on the user's system and installation type.
"""
