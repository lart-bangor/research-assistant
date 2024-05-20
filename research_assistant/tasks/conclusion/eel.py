"""Exposes the Conclusion screen to Python Eel."""
import logging
from typing import Literal
from uuid import UUID

from ...booteel.task_api import ResearchTaskAPI
from ...config import config
from .datamodel import ConclusionTaskResponse

logger = logging.getLogger(__name__)


class ConclusionTaskAPI(ResearchTaskAPI):
    """Eel API for the Conclusion Task."""

    logger = logger
    response_class = ConclusionTaskResponse
    task_version = "0.5.0a0"
    task_data_path = config.paths.data / "Conclusion"
    eel_namespace = "conclusion"

    # No data collected, so it's sufficient to provide the bare basic
    # ResearchTaskAPI. We overwrite store() to ensure data is never stored.

    @ResearchTaskAPI.exposed
    def store(self, response_id: str | UUID) -> Literal[True] | None:
        """Dummy method to avoid storing the dummy ConclusionTaskResponse data model."""
        response_id = self._cast_uuid(response_id)
        self.logger.info(
            f"Request to store data for {self.__class__.__name__} response with id {response_id}..."
            "... skipped: this task only has a dummy data model which should not be stored."
        )
        return True


# Required so importers know which class defines the API
eel_api = ConclusionTaskAPI
