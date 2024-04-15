"""Regular expressions for various data types used by the L'ART Research Assistant."""
from typing import Final

UUID: Final[str] = r"^(?:[0-9]{39})|(?:(?:(?:urn:)?uuid:|{)?[0-9a-fA-F]{8}-?(?:[0-9a-fA-F]{4}-?){3}[0-9a-fA-F]{12}}?)$"  # noqa: E501
"""Regular expression for UUIDs.

Matches UUIDs in hexadecimal, URN and Windows GUID formats.

Examples: :code:`123e4567-e89b-12d3-a456-426614174000`,
    :code:`urn:uuid:123e4567-e89b-12d3-a456-426614174000`,
    :code:`{123e4567-e89b-12d3-a456-426652340000}`,
    :code:`00112233445566778899aabbccddeeff`,
    :code:`000088962710306127702866241727433142015`
"""

UUID_HEX: Final[str] = r"^[0-9a-fA-F]{8}-?(?:[0-9a-fA-F]{4}-?){3}[0-9a-fA-F]{12}$"
"""Regular expression for UUIDs in hexadecimal format.

Matches UUIDs in hexadecimal format, with our without separators.

Examples: :code:`123e4567-e89b-12d3-a456-426614174000`,
    :code:`00000000-0000-0000-0000-000000000000`,
    :code:`00112233445566778899aabbccddeeff`
"""

UUID_INT: Final[str] = r"^[0-9]{39}$"
"""Regular expression for UUIDs in integer (base 10) format.

Does not allow any separators.

.. note::

    Integer UUIDs must be strings with exactly 39 digits, potentially with
    leading zeros. A common source of error is that converting a hexadecimal
    UUID to an integer by simple numeric conversion will yield a number without
    leading zeros and thus fewer than 39 digits.

Examples: :code:`000088962710306127702866241727433142015`
"""

UUID_URN: Final[str] = r"^(?:urn:)?uuid:[0-9a-fA-F]{8}-?(?:[0-9a-fA-F]{4}-?){3}[0-9a-fA-F]{12}$"  # noqa: E501
"""Regular expression for UUIDs in URN format.

Example: :code:`urn:uuid:123e4567-e89b-12d3-a456-426614174000`
"""

GUID: Final[str] = r"^{?[0-9a-fA-F]{8}-?(?:[0-9a-fA-F]{4}-?){3}[0-9a-fA-F]{12}}?$"
"""Regular expression matching a Windows GUID.

Windows GUIDs are hexadecimal UUIDs enclosed by two curly brackets.

Example: :code:`{123e4567-e89b-12d3-a456-426652340000}`
"""

ISO_DAY: Final[str] = r"^(0[1-9]|[12][0-9]|3[01])$"
"""Regular expression matching ISO numeric day strings.

Matches any number string from :code:`01` through :code:`31`.

Examples: :code:`01`, :code:`07`, :code:`12`, :code:`31`
"""

ISO_MONTH: Final[str] = r"^(0[1-9]|1[0-2])$"
"""Regular expression matching ISO numeric month strings.

Matches any number string from :code:`01` through :code:`12`.

Examples: :code:`01`, :code:`07`, :code:`12`
"""

ISO_YEAR: Final[str] = r"^[0-9]{4}$"
"""Regular expression matching ISO numeric year strings.

Matches any number string from :code:`0000` through :code:`9999`.

This does not currently allow for dates before 1 BCE or after 9999 CE, but may
be expanded in the future to allow these.

Examples: :code:`0000`, :code:`0001`, :code:`1569`, :code:`2023`, :code:`9999`
"""

ISO_YEAR_MONTH: Final[str] = r"^[0-9]{1,4}\-(0[1-9]|1[0-2])$"
"""Regular expression matching ISO year-month strings.

Matches ISO date strings of the form YYYY-MM, with the same limitations as for
:code:`ISO_YEAR` noted there.

Examples: :code:`0000-01`, :code:`2023-05`
"""

ISO_YEAR_MONTH_DAY: Final[str] = r"^[0-9]{1,4}\-(0[1-9]|1[0-2])\-(0[1-9]|[12][0-9]|3[01])$"
"""Regular expression matching ISO year-month strings.

Matches ISO date strings of the form YYYY-MM, with the same limitations as for
:code:`ISO_YEAR` noted there.

Examples: :code:`0000-01-01`, :code:`2023-05-31`
"""

TASK_LOCALISATION_LABEL: Final[str] = r"^([A-Z][a-z]{2}){2,}_[A-Z][a-z]{2}_[A-Z]{2}(\.\w*)?"
"""Regular expression for task localisation labels.

Localisation labels consist of three obligatory and one optional parts:

1. Two or more ISO 639 Alpha-3 codes for the language(s) targeted by the localisation.
   These should have the initial letter capitalised, the remaining letters in lower case.
   Use :code:`Und` for *undetermined* languages (e.g. a partially generic localisation).
   The code :code:`Mis` can be used for a language which does not have a code assigned yet,
   but in principle could be assigned a code (though it will be preferable to code a relevant
   macrolanguage where possible). The Codes :code:`Mul` (multiple languages where a single code
   cannot be applied sensibly) and :code:`zxx` (non-linguistic content/language code not
   applicable) should probably be avoided altogether.
2. One ISO 639 Alpha-3 code for the display language of the localisation.
   Follow the same coding guideline as for (1) above.
3. An all-uppercase ISO 3166 Alpha-2 code to indicate the (approximate) location for which
   the localisation is applicable.
4. Optionally a full stop followed by an alphanumeric (A-Za-z0-9_) descriptor, which can be
   used to further specify otherwise similarly labelled localisations (e.g. multiple options
   for a consent form). Note that these are currently ignored for task localisation
   transitions (so a task with localisation AaaBbb_Aaa_AA.foo will simply propagate AaaBbb_Aaa_AA
   as a localisation) - this is so duplicate localisations are not needed for all possible
   task sequences, but may be subject to change in future.

Examples: :code:`ZzzZzz_Zzz_ZZ`, :code:`XxxYyyZzz_Yyy_AA.foo`
"""

SOFTWARE_VERSION_NUMBER: Final[str] = r"^(?:\d+.)*\d+\w?\w?\d*$"
"""Regular expression for software version numbers.

Examples: :code:`0.1.2rc45`, :code:`3`, :code:`0.1.4a`
"""

SOFTWARE_LOCALE_STRING: Final[str] = r"^[a-z]{2}_[A-Z]{2}$"
"""Regular expression for software locale strings.

Examples: :code:`en_US`, :code:`de_BE`
"""

SHORT_ID: Final[str] = r"^[A-Za-z0-9]{3,10}$"
"""Regular expression for short alphanumeric ID strings.

Accepts any string consisting of A-Z, a-z, and 0-9 with a length between 3 and
10 characters.

Examples: :code:`Jane`, :code:`M123X`
"""

SHORT_TEXT: Final[str] = r"^.{0,255}$"
"""Regular expression for short text fields between 0 and 255 characters."""

LONG_TEXT: Final[str] = r"^.*$"
"""Regular expression for text fields of any length."""

ANY_STR: Final[str] = LONG_TEXT
"""Alias for :obj:`LONG_TEXT`."""

LOCATION_NAME: Final[str] = r"^[\w,' \(\)\.\-]{1,50}$"
"""Regular expression for location/place names.

Examples: :code:`Stoke-on-Trent`, :code:`Freiburg (Brsg.)`, :code:`Nürnberg`
"""

LANGUAGE_NAME: Final[str] = r"^[\w][\w\-_ \(\)]{1,50}$"
"""Regular expression for language names."""
