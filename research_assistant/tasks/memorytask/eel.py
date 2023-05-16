"""API to expose the Memory Task to Python Eel."""
import logging
from uuid import UUID
from typing import Any
from ...task_api import ResearchTaskAPI
from ...config import config
from .datamodel import MemoryTaskResponse, MemoryTaskScore

logger = logging.getLogger(__name__)


class MemoryTaskAPI(ResearchTaskAPI):
    """Eel API for the Memory Task."""

    logger = logger
    response_class = MemoryTaskResponse
    task_version = "0.5.0a0"
    task_data_path = config.paths.data / "MemoryTask"
    eel_namespace = "memorytask"

    @ResearchTaskAPI.exposed
    def add_scores(self, response_id: str | UUID, data: dict[str, Any]) -> None:
        """Add scores from Memory to the response with id *response_id*."""
        response_id = self._cast_uuid(response_id)
        self.logger.info(
            f"Adding scores for {self.__class__.__name__} response with id {response_id}.."
        )
        if response_id not in self._response_data:
            exc = ValueError(
                f"Failed to add scores to {self.__class__.__name__} response with id "
                f"{response_id}: no response with this id in progress."
            )
            self.logger.error(str(exc))
            raise exc
        if 'scores' not in data or not isinstance(data['scores'], list):
            exc = KeyError(
                f"Failed to add scores to {self.__class__.__name__} response: ",
                "key 'scores' missing or not a list."
            )
            self.logger.error(str(exc))
            raise exc
        self.logger.debug(f"... score data: {data}")
        for x in data["scores"]:
            missing = self._find_missing_keys(x, ("score", "time"))
            if missing:
                exc = KeyError(
                    f"Failed to add scores to {self.__class__.__name__} response: ",
                    "missing key {missing!r} on at least on score record."
                )
                self.logger.error(str(exc))
                raise exc
            score = MemoryTaskScore(score=x["score"], time=x["time"])
            if "scores" not in self._response_data[response_id]:
                self._response_data[response_id]["scores"] = []
            self._response_data[response_id]["scores"].append(score)

        # This completes the Memory task, so store and finish up...
        if self.store(response_id):
            self.set_location(f"end.html?instance={response_id!s}")


# Required so importers know which class defines the API
eel_api = MemoryTaskAPI
