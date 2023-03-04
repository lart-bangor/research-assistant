"""Additional validation patterns for LSBQe."""
from ..datavalidator.patterns import *                                          # noqa: F401, F403
from ..datavalidator.types import PolarT, EnumT, RangeT, PatternT

LOCATION_NAME: str = r"[\w,' \(\)\.\-]{1,50}"

VERSION_LABEL: str = r"\w{13,17}"

SHORT_ID: str = r"[A-Za-z0-9]{3,10}"

ACQUISITION_SOURCE_HOME: PolarT = (
    {True, "true", "on", "yes", 1, "1", "home", "h"},  # truthy
    {False, "false", "off", "no", 0, "0", "school", "s", "community", "c", "other", "o"}  # falsy
)

ACQUISITION_SOURCE_SCHOOL: PolarT = (
    {True, "true", "on", "yes", 1, "1", "school", "s"},  # truthy
    {False, "false", "off", "no", 0, "0", "home", "h", "community", "c", "other", "o"}  # falsy
)

ACQUISITION_SOURCE_COMMUNITY: PolarT = (
    {True, "true", "on", "yes", 1, "1", "community", "c"},  # truthy
    {False, "false", "off", "no", 0, "0", "home", "h", "school", "s", "other", "o"}  # falsy
)

ACQUISITION_SOURCE_OTHER: PolarT = (
    {True, "true", "on", "yes", 1, "1", "other", "o"},  # truthy
    {False, "false", "off", "no", 0, "0", "home", "h", "school", "s", "community", "c"}  # falsy
)

ACQUISITION_AGE: RangeT = (0, 100)

# Are there any shorter than 3 (Ido)?
LANGUAGE_NAME: PatternT = r"[\w][\w\-_ \(\)]{2,50}"                             # noqa: F405
