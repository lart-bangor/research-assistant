"""Data schema implementing the AGT."""
import logging
import uuid
from random import shuffle
from typing import Any, Optional, TYPE_CHECKING, Final, Callable
from ..datavalidator.schemas import DataSchema
from ..datavalidator.types import PolarT
from . import patterns

logger = logging.getLogger(__name__)

agt_practice_trials: Final[tuple[str, ...]] = (
    "practice",     # Practice trial
)

agt_filler_trials: Final[tuple[str, ...]] = (
    "f1",           # Filler 1
    "f2",           # Filler 2
    "f3",           # Filler 3
    "f4",           # Filler 4
)

agt_guise_trials: Final[tuple[str, ...]] = (
    "s1_maj",    # 1st recording of variety 1
    "s1_rml",    # 1st recording of variety 2
    "s2_maj",    # 2nd recording of variety 1
    "s2_rml",    # 2md recording of variety 2
    "s3_maj",    # 3rd recording of variety 1
    "s3_rml",    # 3rd recording of variety 2
    "s4_maj",    # 4th recording of variety 1
    "s4_rml",    # 4th recording of variety 2
)

agt_trials: Final[tuple[str, ...]] = agt_practice_trials + agt_filler_trials + agt_guise_trials

agt_traits: Final[tuple[str, ...]] = (
    "amusing",
    "open-minded",
    "attractive",
    "trustworthy",
    "ignorant",
    "polite",
    "ambitious",
    "international",
    "cool",
    "intelligent",
    "influential",
    "likeable",
    "educated",
    "friendly",
    "honest",
    "competent",
    "natural",
    "pretentious",
)


class Response(DataSchema):
    """Class for representing the data of an AGT questionnaire response."""
    __schema = {
        "id": {
            "type_": str,
            "typedesc": "AGT Response ID",
            "constraint": patterns.UUID_HEX,
        },
        "meta": {  # Meta data
            "version_id": {
                "type_": str,
                "typedesc": "AGT version identifier",
                "constraint": patterns.VERSION_LABEL,
            },
            "version_no": {
                "type_": str,
                "typedesc": "AGT version number",
                "constraint": patterns.VERSION_NUMBER,
            },
            "app_version": {
                "type_": str,
                "typedesc": "Version of app that last modified the Response",
                "constraint": patterns.VERSION_NUMBER,
            },
            "researcher_id": {
                "type_": str,
                "typedesc": "Researcher ID",
                "constraint": patterns.SHORT_ID,
            },
            "research_location": {
                "type_": str,
                "typedesc": "location name",
                "constraint": patterns.LOCATION_NAME,
            },
            "participant_id": {
                "type_": str,
                "typedesc": "Participant ID",
                "constraint": patterns.SHORT_ID,
            },
            "consent": {
                "type_": PolarT,
                "typedesc": "consent confirmation",
                "constraint": patterns.BOOLEAN,
            },
            "date": {
                "type_": str,
                "typedesc": "current date",
                "constraint": patterns.ISO_YEAR_MONTH_DAY,
            },
        },
        "trial_order": {
            "type_": str,
            "typedesc": "presentation order of trials",
            "constraint": patterns.SHORT_TEXT,
            "required": True,
            "multiple": True,
        },
        "s1_maj_ratings": {
            label: {
                "type_": float,
                "typedesc": f"rating of {label}",
                "constraint": (0, 100)
            } for label in agt_traits
        },
        "s1_rml_ratings": {
            label: {
                "type_": float,
                "typedesc": f"rating of {label}",
                "constraint": (0, 100)
            } for label in agt_traits
        },
        "s2_maj_ratings": {
            label: {
                "type_": float,
                "typedesc": f"rating of {label}",
                "constraint": (0, 100)
            } for label in agt_traits
        },
        "s2_rml_ratings": {
            label: {
                "type_": float,
                "typedesc": f"rating of {label}",
                "constraint": (0, 100)
            } for label in agt_traits
        },
        "s3_maj_ratings": {
            label: {
                "type_": float,
                "typedesc": f"rating of {label}",
                "constraint": (0, 100)
            } for label in agt_traits
        },
        "s3_rml_ratings": {
            label: {
                "type_": float,
                "typedesc": f"rating of {label}",
                "constraint": (0, 100)
            } for label in agt_traits
        },
        "s4_maj_ratings": {
            label: {
                "type_": float,
                "typedesc": f"rating of {label}",
                "constraint": (0, 100)
            } for label in agt_traits
        },
        "s4_rml_ratings": {
            label: {
                "type_": float,
                "typedesc": f"rating of {label}",
                "constraint": (0, 100)
            } for label in agt_traits
        },
        "f1_ratings": {
            label: {
                "type_": float,
                "typedesc": f"rating of {label}",
                "constraint": (0, 100)
            } for label in agt_traits
        },
        "f2_ratings": {
            label: {
                "type_": float,
                "typedesc": f"rating of {label}",
                "constraint": (0, 100)
            } for label in agt_traits
        },
        "f3_ratings": {
            label: {
                "type_": float,
                "typedesc": f"rating of {label}",
                "constraint": (0, 100)
            } for label in agt_traits
        },
        "f4_ratings": {
            label: {
                "type_": float,
                "typedesc": f"rating of {label}",
                "constraint": (0, 100)
            } for label in agt_traits
        },
        "practice_ratings": {
            label: {
                "type_": float,
                "typedesc": f"rating of {label}",
                "constraint": (0, 100)
            } for label in agt_traits
        },
    }

    def __init__(self, id_: Optional[str] = None):
        """Instantiates a new LSBQ-RML response object."""
        super().__init__(forcecast=True, ignorecase=True)
        if id_ is None:
            id_ = str(uuid.uuid1())
        self.setid(id_)

    def setratings(self, trial: str, ratings: dict[str, float]):
        """Set the ratings for the trial labelled by *trial*."""
        if not hasattr(self, f"set{trial}_ratings"):
            raise ValueError(f"{trial!r} is not a known trial id.")
        setter: Callable[[Any], None] = getattr(self, f"set{trial}_ratings")
        setter(ratings)

    def getratings(self, trial: str) -> dict[str, float]:
        """Get the ratings for the trial labelled by *trial*."""
        if not hasattr(self, f"get{trial}_ratings"):
            raise ValueError(f"{trial!r} is not a known trial id.")
        getter: Callable[[], dict[str, float]] = getattr(self, f"get{trial}_ratings")
        return getter()

    def generate_trial_order(
        self,
        fillers: list[str] | None = None,
        speakers: list[str] | None = None,
        languages: list[str] | None = None,
        sep: str = "_"
    ) -> tuple[str, ...]:
        """Produce a pseudo-randomised AGT presentation order.

        Given four speakers, four fillers, and two languages,
        produce a presentation order for Matched Guise Task,
        based on the following grid:

        +---------+----------+-----------------------+
        | Speaker | Language | Example               |
        +---------+----------+-----------------------+
        | F1      | Either   | Filler 1              |
        | S1      | L1       | Speaker 1, Language 1 |
        | S2      | L2       | Speaker 2, Language 2 |
        | F2      | Either   | Filler 2              |
        | S3      | L2       | Speaker 3, Language 2 |
        | S4      | L1       | Speaker 4, Language 1 |
        | F3      | Either   | Filler 3              |
        | S1      | L2       | Speaker 1, Language 2 |
        | S2      | L1       | Speaker 2, Language 1 |
        | F4      | Either   | Filler 4              |
        | S3      | L1       | Speaker 3, Language 1 |
        | S4      | L2       | Speaker 4, Language 2 |
        +---------+----------+-----------------------+

        The function randomises:
            (a) the order of the fillers (regardless of filler language),
            (b) the order in which speakers are presented (distance kept constant)
            (c) whether L1 or L2 are presented first (keeping alternation constant)
        """
        # Validate parameters
        if fillers is None:
            fillers = ["f1", "f2", "f3", "f4"]
        if speakers is None:
            speakers = ["s1", "s2", "s3", "s4"]
        if languages is None:
            languages = ["maj", "rml"]
        if len(fillers) != 4 or len(speakers) != 4 or len(languages) != 2:
            raise ValueError(
                "Wrong list length for parameters. "
                "Need 4 fillers, 4 speakers, 2 languages."
            )
        # Randomise parameters
        shuffle(fillers)
        shuffle(speakers)
        shuffle(languages)
        # Build order
        order: tuple[str, ...] = (
            fillers[0],
            f"{speakers[0]}{sep}{languages[0]}",
            f"{speakers[1]}{sep}{languages[1]}",
            fillers[1],
            f"{speakers[2]}{sep}{languages[1]}",
            f"{speakers[3]}{sep}{languages[0]}",
            fillers[2],
            f"{speakers[0]}{sep}{languages[1]}",
            f"{speakers[1]}{sep}{languages[0]}",
            fillers[3],
            f"{speakers[2]}{sep}{languages[0]}",
            f"{speakers[3]}{sep}{languages[1]}",
        )
        return order

    if TYPE_CHECKING:  # noqa: C901

        def setid(self, id: str) -> None:
            """Set the id of the AGT instance."""
            ...

        def getid(self) -> str:
            """Get the id of the AGT instance."""
            ...

        def setmeta(self, *args: Any) -> None:
            """Set the meta data of the AGT instance."""
            ...

        def getmeta(self) -> dict[str, Any]:
            """Get the meta data of the AGT instance."""
            ...

        def gettrial_order(self) -> list[str]:
            """Get the order of trials for the AGT instance."""
            ...
