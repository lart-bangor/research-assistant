"""Additional validation patterns for AToL-C."""
from ..datavalidator.patterns import *  # noqa: F403

LOCATION_NAME: str = r"[\w,' \(\)\.\-]{1,50}"

VERSION_LABEL: str = r"\w{13,17}"

SHORT_ID: str = r"[A-Za-z0-9]{3,10}"

ACQUISITION_SOURCE: EnumT = {  # noqa: F405
    "home":      "h",
    "h":         "h",
    "school":    "s",
    "s":         "s",
    "community": "c",
    "c":         "c",
    "other":     "o",
    "o":         "o",
}

LANGUAGE_NAME: PatternT = r"\w{3,50}"  # noqa: F405  # Are there any shorter than 3 (Ido)?
