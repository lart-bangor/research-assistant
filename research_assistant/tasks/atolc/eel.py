"""API to expose the AToL-C Task to Python Eel."""
import logging
from uuid import UUID
from typing import Any
from ...task_api import ResearchTaskAPI
from ...config import config
from .datamodel import AtolcTaskLanguageRatings, AtolcTaskResponse

logger = logging.getLogger(__name__)


class AtolcTaskAPI(ResearchTaskAPI):
    """Eel API for the AToL-C Task."""

    logger = logger
    response_class = AtolcTaskResponse
    task_version = "0.5.0a0"
    task_data_path = config.paths.data / "AToL-C"
    eel_namespace = "atolc"

    atolc_traits = (
        "logic",      "elegance",  "fluency",
        "ambiguity",  "appeal",    "structure",
        "precision",  "harshness", "flow",
        "beauty",     "sistem",    "pleasure",
        "smoothness", "grace",     "angularity"
    )

    @ResearchTaskAPI.exposed
    def get_traits(self) -> list[str]:
        """Return a list of the AToL-C traits."""
        return list(self.atolc_traits)

    @ResearchTaskAPI.exposed
    def add_ratings(self, response_id: str | UUID, data: dict[str, Any]) -> None:  # noqa: C901
        """Add AToL-C ratings to the response with id *response_id*."""
        response_id = self._cast_uuid(response_id)
        self.logger.info(
            f"Adding ratings for {self.__class__.__name__} response with id {response_id}.."
        )
        if response_id not in self._response_data:
            exc = ValueError(
                f"Failed to add ratings to {self.__class__.__name__} response with id "
                f"{response_id}: no response with this id in progress."
            )
            self.logger.error(str(exc))
            raise exc
        self.logger.debug(f"... ratings data: {data}")
        if "language" not in data:
            exc = KeyError(
                f"Failed to add ratings to {self.__class__.__name__} response: "
                "missing 'language' value."
            )
            self.logger.error(str(exc))
            raise exc
        ratings: dict[str, float] = dict()
        for key, value in data.items():
            if key.startswith("trait-"):
                ratings[key.removeprefix("trait-")] = float(value)
        missing = self._find_missing_keys(
            ratings,
            self.atolc_traits
        )
        if missing:
            exc = KeyError(
                f"Failed to add ratings to {self.__class__.__name__} response: "
                "missing key {missing!r} for at least one trait."
            )
            self.logger.error(str(exc))
            raise exc
        ratings = AtolcTaskLanguageRatings(language=data["language"], **ratings)
        if "ratings" not in self._response_data[response_id]:
            self._response_data[response_id]["ratings"] = []
        self._response_data[response_id]["ratings"].append(ratings)


# Required so importers know which class defines the API
eel_api = AtolcTaskAPI
