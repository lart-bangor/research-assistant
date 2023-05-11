"""API Base implementing typical functionality for a L'ART Research Assistant task."""
import logging
import json
from typing import Any, Type, Iterable, Literal
from uuid import UUID, uuid1
from importlib import resources
from pathlib import Path
from pydantic import ValidationError
from .datamodels.models import ResponseBase, ResponseMetadata
from .datamodels.utils import validation_error_to_html
from . import booteel
from .booteel.eel_api import EelAPI
from .config import config

logger = logging.getLogger(__name__)


class ResearchTaskAPI(EelAPI):
    """Base class for EelAPIs exposing a Research Assistant task."""

    logger: logging.Logger = logger
    response_class: Type[ResponseBase]
    task_version: str
    task_data_path: Path
    _response_data: dict[UUID, dict[str, Any]]
    _required_fields: set[str]
    _localisations_available: dict[str, str]
    _localisation_data: dict[str, dict[Any]]

    def __init__(self):
        """Initialise the EelTaskAPI."""
        self._response_data = {}
        self._required_fields = self._get_required_fields(self.response_class)
        self._localisations_available = {}
        self._localisation_data = {}

    def _get_required_fields(self, model: Type[ResponseBase]) -> set[str]:
        required_fields: set[str] = set()
        for name, field in model.__fields__.items():
            if field.required:
                required_fields.add(name)
        return required_fields

    @classmethod
    def exception_handler(cls, exc: Exception) -> None:
        """Handle exceptions by logging and passing them to the frontend via booteel."""
        if isinstance(exc, ValidationError):
            booteel.modal(
                "Data Validation Error",
                validation_error_to_html(exc),
                icon="database-exclamation"
            )
        else:
            booteel.displayexception(exc)
        cls.logger.exception(exc)

    @EelAPI.exposed
    def get_localisations(self) -> dict[str, str]:
        """Get a dictionary of available task localisations.

        Returns a dictionary with the localisation's label as key and its
        description as value.

        Looks for the localisations as part of the package data in the
        :code:`localisations` subpackage of the :code:`__module__` where the API
        is defined.

        The localisations are lazy-loaded when :func:`get_localisations()` is
        first called.
        """
        if len(self._localisations_available) > 0:
            return self._localisations_available

        resource_target = ".".join((self.__module__, "localisations"))
        for item in resources.contents(resource_target):
            if not (resources.is_resource(resource_target, item)
                    and item[0] != "_"
                    and item[-5:] == ".json"):
                continue  # Not a JSON file or marked internal
            with resources.open_text(resource_target, item) as fp:
                buf = json.load(fp)
                if "meta" in buf and "versionId" in buf["meta"] and "versionName" in buf["meta"]:
                    label, description = buf["meta"]["versionId"], buf["meta"]["versionName"]
                    self._localisations_available[label] = description
                else:
                    self.logger.error(
                        f"Resource '{resource_target}/{item}' is missing one of the required keys "
                        "'meta.versionId' or 'meta.versionName'."
                    )

    @EelAPI.exposed
    def load_localisation(
        self,
        label: str,
        sections: list[str]
    ) -> dict[str, dict[str, Any]]:
        """Load the localisation indicated by *label*, if available.

        The localisations are lazy-loaded the first time the localisation with
        *label* are loaded using :func:`load_localisation()`. All sections are
        loaded when this happens, irrespective of the value of *sections*.
        """
        # Lazy-load localisation data if needed
        if label not in self._localisation_data:
            if self._localisations_available == 0:
                self.get_localisations()  # Might not have been called yet
            resource_target = ".".join((self.__module__, "localisations"))
            if label not in self._localisations_available:
                self.logger.warning(
                    f"Attempting to load non-existent localistion {label} for "
                    f"{self.__class__.__name__} from package {resource_target}."
                )
                return {}
            if not resources.is_resource(resource_target, f"{label}.json"):
                self.logger.error(
                    f"Failed to hard-load localisation {label} for "
                    f"{self.__class__.__name__} from package {resource_target}: "
                    f"resource '{label}.json' does not exist."
                )
                return {}
            buffer = None
            with resources.open_text(resource_target, f"{label}.json") as fp:
                buffer = json.load(fp)
            if not isinstance(buffer, dict):
                self.logger.error(
                    f"Failed to hard-load localisation {label} for "
                    f"{self.__class__.__name__} from package {resource_target}: "
                    f"invalid file format or corrupt file."
                )
                return {}
            self._localisation_data[label] = buffer
            self.logger.debug(
                f"Hard-loaded localisation {label} data for "
                f"{self.__class__.__name__} from package {resource_target}."
            )

        # Return appropriate sections of localisation data
        buffer: dict[str, dict[str, Any]] = {}
        for section in sections:
            if section in self._localisation_data[label]:
                buffer[section] = self._localisation_data[label][section]
        return buffer

    @staticmethod
    def _find_missing_keys(d: dict[Any, Any], required: Iterable[Any]) -> set[Any]:
        missing = set()
        for key in required:
            if key not in d:
                missing.add(key)
        return missing

    @staticmethod
    def _cast_uuid(uuid: str | UUID) -> UUID:
        return uuid if isinstance(uuid, UUID) else UUID(uuid)

    @EelAPI.exposed
    def new(self, data: dict[str, Any]) -> str:
        """Initialise a new Task response.

        The *data* argument must be a dictionary containing at least the
        following keys:
        - *selectSurveyVersion*
        - *researcherId*
        - *participantId*
        - *confirmConsent*
        """
        self.logger.info(f"Creating new {self.__class__.__name__} response..")
        response_id = uuid1()
        self.logger.info(f"... response_id={response_id}")
        self.logger.debug(f"... data={data!r}")
        missing = self._find_missing_keys(
            data,
            ("selectSurveyVersion", "researcherId", "participantId", "confirmConsent")
        )
        if missing:
            exc = KeyError(
                f"Failed to create new {self.__class__.__name__} response: "
                f"missing keys {missing!r}."
            )
            self.logger.error(str(exc))
            raise exc
        meta = ResponseMetadata(
            task_localisation=data["selectSurveyVersion"],
            task_version_no=self.task_version,
            app_version_no=config.appversion,
            app_system_useragent="Unknown",  # @TODO
            app_display_language="en_GB",    # @TODO
            researcher_id=data["researcherId"],
            research_location=data["researchLocation"],
            participant_id=data["participantId"],
            consent_obtained=data["confirmConsent"]
        )
        self.logger.debug(f"... meta={meta!r}")
        self._response_data[response_id]["id"] = response_id
        self._response_data[response_id]["meta"] = meta
        self.logger.debug("... success.")
        return str(response_id)

    @EelAPI.exposed
    def discard(self, response_id: str | UUID) -> Literal[True] | None:
        """Discard all data for response with id *response_id*."""
        response_id = self._cast_uuid(response_id)
        self.logger.info(
            f"Discarding {self.__class__.__name__} response with id {response_id}.."
        )
        if response_id not in self._response_data:
            exc = ValueError(
                f"Failed to discard data for {self.__class__.__name__} response with id "
                f"{response_id}: no response with this id in progress."
            )
            self.logger.error(str(exc))
            raise exc
        del self._response_data[response_id]
        self.logger.debug("... success.")
        return True

    @EelAPI.exposed
    def is_complete(self, response_id: str | UUID) -> bool | None:
        """Check whether response with id *response_id* is complete."""
        response_id = self._cast_uuid(response_id)
        self.logger.info(
            f"Check completeness of {self.__class__.__name__} response with id {response_id}.."
        )
        if response_id not in self._response_data:
            exc = ValueError(
                f"Failed to check data for {self.__class__.__name__} response with id "
                f"{response_id}: no response with this id in progress."
            )
            self.logger.error(str(exc))
            raise exc
        for field in self._required_fields:
            if field not in self._response_data[response_id]:
                self.logger.info(f"... response is incomplete - missing {field} (possibly more).")
                return False
        self.logger.info("... response is complete.")
        return True

    @EelAPI.exposed
    def store(self, response_id: str | UUID) -> Literal[True] | None:
        """Submit a complete response to long-term storage."""
        response_id = self._cast_uuid(response_id)
        self.logger.info(
            f"Storing data for {self.__class__.__name__} response with id {response_id}.."
        )
        if not self.is_complete(response_id):
            exc = ValueError(
                f"Failed to store data for {self.__class__.__name__} response with id "
                f"{response_id}: response is incomplete."
            )
            self.logger.error(str(exc))
        response = self.response_class(**self._response_data[response_id])
        json = response.json()
        self.logger.debug(f"... JSON serialization: {json}")
        path = self.task_data_path / str(response.meta.task_localisation)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        filename = path / f"{response.meta.participant_id!s}_{response_id!s}.json"
        self.logger.debug(f"... writing to file: {filename}")
        with filename.open("w") as fp:
            fp.write(json)
        self.logger.debug("... success.")

    @EelAPI.exposed
    def end(self, response_id: str | UUID, data: dict[str, Any] | None = None) -> str:
        """Redirect participant to next task in sequence and remove current response from memory.

        .. important::

            Response data for *response_id* is discarded from memory once :func:`end()` is called.
            You **must** call :func:`store()` before callind :func:`end()` to store the data.
        """
        response_id = self._cast_uuid(response_id)
        self.logger.info(
            f"Redirect participant after {self.__class__.__name__} response with id {response_id}.."
        )
        if response_id not in self._response_data:
            exc = ValueError(
                f"Failed to retrieve data for {self.__class__.__name__} response with id "
                f"{response_id}: no response with this id in progress."
            )
            self.logger.error(str(exc))
            raise exc
        if not self.is_complete(response_id):
            exc = ValueError(
                f"Failed to redirect participant: data for {self.__class__.__name__} response "
                f"with id  {response_id} is incomplete."
            )
            self.logger.error(str(exc))
            raise exc
        if hasattr(config.sequences, self.__class__.__module__):
            self.logger.debug("... sequencing information found.")
            response_meta = self._response_data[response_id]["meta"]
            query = booteel.buildquery({
                "selectSurveyVersion": str(response_meta.task_localisation),
                "researcherId": str(response_meta.researcher_id),
                "researchLocation": str(response_meta.research_location),
                "confirmConsent": str(response_meta.consent_obtained),
                "surveyDataForm.submit": "true",
            })
            href = f"/app/{getattr(config.sequences, self.__class__.__module__)}/index.html?{query}"
            self.logger.debug(f"... redirecting to: {href}")
            booteel.setlocation(href)
        else:
            href = "/app/index.html"
            self.logger.debug("... no sequencing information found.")
            self.logger.debug(f"... redirecting to: {href}")
            booteel.setlocation(href)
        self.discard(response_id)
        return href
