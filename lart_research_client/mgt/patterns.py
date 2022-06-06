"""Additional validation patterns for LSBQ-RML."""
from ..datavalidator.patterns import *                                          # noqa: F401, F403
from ..datavalidator.types import EnumT, RangeT, PatternT

LOCATION_NAME: str = r"[\w, \(\)]{1,50}"

VERSION_LABEL: str = r"\w{13,17}"

SHORT_ID: str = r"[A-Za-z0-9]{3,10}"
