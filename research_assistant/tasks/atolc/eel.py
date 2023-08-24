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
        MAX_TRIALS = 2
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
        if "languageTrial" not in data:
            exc = KeyError(
                f"Failed to add ratings to {self.__class__.__name__} response: "
                "missing 'languageTrial' value."
            )
            self.logger.error(str(exc))
            raise exc
        language_trial = int(data["languageTrial"])
        if language_trial < 0 or language_trial > MAX_TRIALS:
            exc = ValueError(
                f"Failed to add ratings to {self.__class__.__name__} response:"
                f"invalid 'languageTrial' value, must be 1 or 2, {language_trial} given."
            )
            self.logger.error(str(exc))
            raise exc
        if "languageName" not in data:
            exc = KeyError(
                f"Failed to add ratings to {self.__class__.__name__} response: "
                "missing 'languageName' value."
            )
            self.logger.error(str(exc))
            raise exc
        language_name = str(data["languageName"])
        trait_ratings: dict[str, float] = dict()
        for key, value in data.items():
            if key.startswith("trait-"):
                trait_ratings[key.removeprefix("trait-")] = float(value)
        missing = self._find_missing_keys(
            trait_ratings,
            self.atolc_traits
        )
        if missing:
            exc = KeyError(
                f"Failed to add ratings to {self.__class__.__name__} response: "
                "missing key {missing!r} for at least one trait."
            )
            self.logger.error(str(exc))
            raise exc
        ratings = AtolcTaskLanguageRatings(
            language=language_name,
            trial=language_trial,
            order=list(trait_ratings.keys()),
            **trait_ratings
        )
        if "ratings" not in self._response_data[response_id]:
            self._response_data[response_id]["ratings"] = []
        self._response_data[response_id]["ratings"].append(ratings)
        if language_trial < MAX_TRIALS:
            self.set_location(f"start.html?instance={response_id}&trial={language_trial+1}")
        elif self.store(response_id):
            self.set_location(f"end.html?instance={response_id}")
        else:
            exc = RuntimeError(
                f"Failed to store {self.response_class.__name__} response with id {response_id}: "
                " reason not known."
            )
            self.logger.error(str(exc))
            raise exc


# Required so importers know which class defines the API
eel_api = AtolcTaskAPI
