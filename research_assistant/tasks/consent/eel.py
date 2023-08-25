"""API to expose the Consent Task to Python Eel."""
import logging
from uuid import UUID
from typing import Any
from ...task_api import ResearchTaskAPI
from ...config import config
from .datamodel import ConsentTaskResponse

logger = logging.getLogger(__name__)


class ConsentTaskAPI(ResearchTaskAPI):
    """Eel API for the Consent Task."""

    logger = logger
    response_class = ConsentTaskResponse
    task_version = "0.5.0a0"
    task_data_path = config.paths.data / "Consent"
    eel_namespace = "consent"


# Required so importers know which class defines the API
eel_api = ConsentTaskAPI
