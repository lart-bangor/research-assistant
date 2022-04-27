"""Data structures for the Memory Game."""
import logging
import uuid
from typing import Any, Optional, TYPE_CHECKING
from ..datavalidator.schemas import DataSchema
from ..datavalidator.types import PolarT
from . import patterns

logger = logging.getLogger(__name__)


class Response(DataSchema):
    """Class for representing the data of a Memory Game."""
    __schema = {
        "id": {
            "type_": str,
            "typedesc": "Memory Game Response ID",
            "constraint": patterns.UUID_HEX,
        },
        "meta": {  # Meta data
            "version": {
                "type_": str,
                "typedesc": "Memory Game version identifier",
                "constraint": patterns.VERSION_LABEL,
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
        "scores": {
            "score": {  # Scores from the memory games played
                "type_": int,
                "typedesc": "score",
                "constraint": patterns.POSITIVE_NUMBER_ZERO,
                "multiple": True,
            },
            "time": {  # Time from the memory games played
                "type_": int,
                "typedesc": "time",
                "constraint": patterns.POSITIVE_NUMBER_ZERO,
                "multiple": True,
            },
        },
    }

    def __init__(self, id_: Optional[str] = None):
        """Instantiates a new LSBQ-RML response object."""
        super().__init__(forcecast=True, ignorecase=True)
        if id_ is None:
            id_ = str(uuid.uuid1())
        self.setid(id_)

    if TYPE_CHECKING:  # noqa: C901

        def setid(self, id: str) -> None:
            """Set the id of the Memory Game instance."""
            ...

        def getid(self) -> str:
            """Get the id of the Memory Game instance."""
            ...

        def setmeta(self, *args: Any) -> None:
            """Set the meta data of the Memory Game instance."""
            ...

        def getmeta(self) -> dict[str, Any]:
            """Get the meta data of the Memory Game instance."""
            ...

        def setscores(self, *args: Any) -> None:
            """Set the scores of the Memory Game instance."""
            ...

        def getscores(self) -> list[int]:
            """Get the scores of the Memory Game instance."""
            ...
