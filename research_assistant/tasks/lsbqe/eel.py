"""API to exposes the LSBQe to Python Eel."""
import logging
from uuid import UUID
from typing import Any
from ...task_api import ResearchTaskAPI
from ...config import config
from .datamodel import LsbqeTaskResponse

logger = logging.getLogger(__name__)


class LsbqeTaskAPI(ResearchTaskAPI):
    """Eel API for the LSBQe Task."""

    logger = logger
    response_class = LsbqeTaskResponse
    task_version = "0.5.0a0"
    task_data_path = config.paths.data / "LSBQe"
    eel_namespace = "lsbqe"


# Required so importers know which class defines the API
eel_api = LsbqeTaskAPI
