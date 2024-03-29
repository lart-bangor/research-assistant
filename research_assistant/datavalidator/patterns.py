"""Patterns/ranges/enums/etc. for validating different common data input types."""
import sys
from .types import PatternT, EnumT, PolarT, RangeT


UUID: PatternT = r"(?:[0-9]{39})|(?:(?:(?:urn:)?uuid:|{)?[0-9a-fA-F]{8}-?(?:[0-9a-fA-F]{4}-?){3}[0-9a-fA-F]{12}}?)"  # noqa: E501

UUID_HEX: PatternT = r"[0-9a-fA-F]{8}-?(?:[0-9a-fA-F]{4}-?){3}[0-9a-fA-F]{12}"

UUID_INT: PatternT = r"[0-9]{39}"

UUID_URN: PatternT = r"(?:urn:)?uuid:[0-9a-fA-F]{8}-?(?:[0-9a-fA-F]{4}-?){3}[0-9a-fA-F]{12}"  # noqa: E501

GUID: PatternT = r"{?[0-9a-fA-F]{8}-?(?:[0-9a-fA-F]{4}-?){3}[0-9a-fA-F]{12}}?"

ISO_MONTH: PatternT = r"(0?[1-9]|1[0-2])"                        # MM

ISO_DAY: PatternT = r"(0?[1-9]|[12][0-9]|3[01])"                 # DD

ISO_YEAR: PatternT = r"[0-9]{1,4}"                               # YYYY

ISO_YEAR_MONTH: PatternT = ISO_YEAR + r"\-" + ISO_MONTH          # YYYY-MM

ISO_YEAR_MONTH_DAY: PatternT = ISO_YEAR_MONTH + r"\-" + ISO_DAY  # YYYY-MM-DD

VERSION_NUMBER: PatternT = r"(?:\d+.)*\d+\w?\w?\d*" # 3, 0.4, 1.0a, 24.2.4rc45 etc.

MONTH_NAME: EnumT = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12,
}

MONTH_NAME_ABBR: EnumT = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12,
}

BOOLEAN: PolarT = (
    {True, "true", "on", "yes", 1, "1"},    # positive/true
    {False, "false", "off", "no", 0, "0"},  # negative/false
)

SEX_BINARY: EnumT = {
    "male":   "m",
    "m":      "m",
    "he":     "m",
    "mr":     "m",
    "mister": "m",
    "female": "f",
    "f":      "f",
    "she":    "f",
    "ms":     "f",
    "mrs":    "f",
    "miss":   "f",
    "missus": "f",
}

SEX_TERNARY: EnumT = SEX_BINARY | {
    "other":  "o",
    "o":      "o",
    "x":      "o",
    "they":   "o",
    "mx":     "o",
}

SHORT_TEXT: PatternT = r".{0,255}"

LONG_TEXT: PatternT = r".*"

ANY_STR: PatternT = LONG_TEXT

HANDEDNESS: EnumT = {
    "lefthanded": "l",
    "left": "l",
    "l": "l",
    "righthanded": "r",
    "right": "r",
    "r": "r",
}

EQF_LEVEL: RangeT = (1, 8)

EQF_LEVEL_NA: RangeT = (0, 8)

LIKERT_4: RangeT = (1, 4)

LIKERT_5: RangeT = (1, 5)

LIKERT_6: RangeT = (1, 6)

LIKERT_7: RangeT = (1, 7)

LIKERT_8: RangeT = (1, 8)

LIKERT_9: RangeT = (1, 9)

LIKERT_10: RangeT = (1, 10)

LIKERT_4_NA: RangeT = (0, 4)

LIKERT_5_NA: RangeT = (0, 5)

LIKERT_6_NA: RangeT = (0, 6)

LIKERT_7_NA: RangeT = (0, 7)

LIKERT_8_NA: RangeT = (0, 8)

LIKERT_9_NA: RangeT = (0, 9)

LIKERT_10_NA: RangeT = (0, 10)

ZERO_ONE_RANGE: RangeT = (0.0, 1.0)

ANY_NUMBER: RangeT = (-sys.maxsize - 1, sys.maxsize)

POSITIVE_NUMBER_ONE: RangeT = (1, sys.maxsize)

POSITIVE_NUMBER_ZERO: RangeT = (0, sys.maxsize)

NEGATIVE_NUMBER_ONE: RangeT = (-1, -sys.maxsize - 1)

NEGATIVE_NUMBER_ZERO: RangeT = (0, -sys.maxsize - 1)
