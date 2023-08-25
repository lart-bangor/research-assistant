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

    @ResearchTaskAPI.exposed
    def record_consent(self, response_id: UUID, data: dict[str, Any]) -> None:
        """Record consent and eligibility data."""
        response_id = self._cast_uuid(response_id)
        self.logger.info(
            f"Adding consent/eligibility data for {self.__class__.__name__} with"
            f"response id {response_id}.."
        )
        if response_id not in self._response_data:
            exc = ValueError(
                f"Failed to add consent/eligibility to {self.__class__.__name__} response with id "
                f"{response_id}: no response with this id in progress."
            )
            self.logger.error(str(exc))
            raise exc
        self.logger.debug(f"... consent/eligibility data: {data}")
        missing = self._find_missing_keys(data, ("confirmInformedConsent", "confirmEligibility"))
        if missing:
            exc = KeyError(
                f"Failed to add consent/eligibility to {self.__class__.__name__} response: "
                f"missing key(s) {missing!r} for at least one trait."
            )
            self.logger.error(str(exc))
            raise exc
        informed_consent = bool(data["confirmInformedConsent"])
        eligibility_confirmed = bool(data["confirmEligibility"])
        self._response_data[response_id]["informed_consent"] = informed_consent
        self._response_data[response_id]["eligibility_confirmed"] = eligibility_confirmed
        # Fix task_localisation (includes ".xyz" for a task group, which needs to be split off)
        response_meta = self._response_data[response_id]["meta"]
        localisation_string: str = response_meta.task_localisation
        task_localisation, consent_task_group = localisation_string.split(".")
        response_meta.task_localisation = task_localisation
        self._response_data[response_id]["consent_task_group"] = consent_task_group
        if self.store(response_id):
            self.end(response_id)
        else:
            exc = RuntimeError(
                f"Failed to store {self.response_class.__name__} response with id {response_id}: "
                "reason unknown."
            )
            self.logger.error(str(exc))
            raise exc


# Required so importers know which class defines the API
eel_api = ConsentTaskAPI
