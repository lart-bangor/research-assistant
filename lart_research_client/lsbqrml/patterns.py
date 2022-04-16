"""Additional validation patterns for LSBQ-RML."""
from datavalidator.types import EnumT, RangeT, PatternT
from datavalidator.patterns import *  # noqa: F401, F403

LOCATION_NAME: str = r"[A-Za-z0-9, \(\)]{1,50}"

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

ACQUISITION_AGE: RangeT = (0, 100)

LANGUAGE_NAME: PatternT = r"[a-zA-Z][a-zA-Z0-9\-_ \(\)]{2,50}"  # noqa: F405  # Are there any shorter than 3 (Ido)?
