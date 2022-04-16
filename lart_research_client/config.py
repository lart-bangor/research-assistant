"""Configuration handler for LART Research Client."""
from __future__ import annotations
from appdirs import AppDirs
from pathlib import Path
from typing import Any, Callable, get_type_hints
from copy import copy
from dataclasses import dataclass, field, fields, asdict, is_dataclass
import json
import logging

__all__ = ["logger", "config"]

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
    """Class for holding App paths."""

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
class Config(DataclassDictMixin):
    """Class for keeping track of App configuration data."""

    appname: str = field(default=_appname, init=False)
    appauthor: str = field(default=_appauthor, init=False)
    paths: Paths = field(default=Paths())

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
