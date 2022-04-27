"""Configuration handler for LART Research Client."""
from __future__ import annotations
import json
import logging
from appdirs import AppDirs
from copy import copy
from dataclasses import dataclass, field, fields, asdict, is_dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional, Union, get_type_hints

__all__ = ["config"]

logger = logging.getLogger(__name__)

_appname: str = "Research Client"
_appauthor: str = "LART"
_default_dirs: AppDirs = AppDirs(_appname, _appauthor, roaming=True)


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
    def fromdict(cls, d: dict[str, Any]):  # noqa: C901
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
                raise ValueError(f"Dataclass {cls!r} has no attribute {name!r}.")
            if is_dataclass(type_map[name]) and isinstance(d[name], dict):
                if hasattr(type_map[name], "fromdict"):
                    value = type_map[name].fromdict(d[name])  # type: ignore
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


@dataclass
class Paths(DataclassDictMixin):
    """Class for configuration of App paths."""

    config: Path = field(default=Path(_default_dirs.user_config_dir), init=False)
    data: Path = field(default=Path(_default_dirs.user_data_dir))
    logs: Path = field(default=Path(_default_dirs.user_log_dir))
    cache: Path = field(default=Path(_default_dirs.user_cache_dir))

    def __post_init__(self):
        """Post-init method that ensures paths are all pathlib Path objects."""
        for field_ in fields(self):
            if field_.type == Path.__name__ and not isinstance(
                getattr(self, field_.name), Path
            ):
                setattr(self, field_.name, Path(getattr(self, field_.name)))

@dataclass
class Logging(DataclassDictMixin):
    """Class for Logging configuration."""

    max_files: int = field(default=10)
    default_level: int = field(default=logging.WARNING)
    stream_format: str = field(default="{levelname}:{name}: {message}")
    file_format: str = field(default="[{asctime} {levelname:<8} {name}] {message}")

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
class Config(DataclassDictMixin):
    """Class for keeping track of App configuration data."""

    appname: str = field(default=_appname, init=False)
    appauthor: str = field(default=_appauthor, init=False)
    paths: Paths = field(default=Paths())
    logging: Logging = field(default=Logging())

    def save(self, filename: str = "settings.json"):
        """Save configuration to a file."""
        path = self.paths.config / filename
        if not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
        d = self.asdict()
        with path.open("w") as fp:
            json.dump(d, fp, indent=4, cls=JSONPathEncoder)

    @classmethod
    def load(cls, filename: str = "settings.json"):
        """Load configuration from a file or return default Config()."""
        path = Path(_default_dirs.user_config_dir) / filename
        if path.exists():
            try:
                with path.open("r") as fp:
                    d = json.load(fp)
                cfg = Config.fromdict(d)
                return cfg
            except Exception as e:
                logging.error(e)
                return Config()
        return Config()


config = Config.load()
