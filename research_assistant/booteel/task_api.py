"""API Base implementing typical functionality for a L'ART Research Assistant task."""

import json
import logging
from importlib import resources
from pathlib import Path
from typing import Any, Iterable, Literal, Type
from uuid import UUID, uuid1

from pydantic import ValidationError

from ..config import config
from ..datamodels.models import ResponseBase, ResponseMetadata
from ..datamodels.types import _T, AnyUUID, KeyT
from ..datamodels.utils import validation_error_to_html
from . import errors
from . import utils as booteel_utils
from .eel_api import EelAPI

logger = logging.getLogger(__name__)


class ResearchTaskAPI(EelAPI):
    """Base class for EelAPIs exposing a Research Assistant task.

    Base class for all Research Assistant tasks. Derived classes
    must minimally set the class variables *response_class*,
    *task_version* and *task_data_path* to appropriate values; they should
    set the class variable *logger* to an appropriate instance of
    `logging.Logger`; and they must call `super().__init__()` if they define
    their own `__init__()` method.

    The `ResearchTaskAPI` pre-defines the following commonly used and expected
    interface methods and exposes them via `eel`:
        * `ResearchTaskAPI.get_localisations()`
        * `ResearchTaskAPI.load_localisation()`
        * `ResearchTaskAPI.new()`
        * `ResearchTaskAPI.discard()`
        * `ResearchTaskAPI.is_complete()`
        * `ResearchTaskAPI.store()`
        * `ResearchTaskAPI.end()`
    They can be overwritten if needed, but it is considered best practice to
    avoid this where possible because it makes debugging more difficult. Note
    also that overwriting an exposed method will trigger an INFO-level message.

    In addition to the above interface methods, a number of convenience methods
    are provided. Where these method names start with a single underscore
    (e.g. `ResearchTaskAPI._cast_uuid()`) they should be considered internal,
    i.e. you can call them from within your subclass, but you should not call
    them from outside a `ResearchTaskAPI`-derived class. Those methods not
    so marked are intended for calling both from within and without the class.
    """

    # Logger used for logging errors originating from the tasks' Eel API.
    logger: logging.Logger = logger
    # The class defining the tasks' top-level Pydantic data model.
    response_class: Type[ResponseBase]
    # The version of the task.
    task_version: str
    # The relative path (directory name) under which the task's data should be stored.
    task_data_path: Path
    # The qualified package name of the task (determined automatically).
    _task_package: str
    # Temporary, possibly incomplete, response data for collation before building
    # the final data model and storing it.
    _response_data: dict[UUID, dict[str, Any]]
    # A set of fields marked as required by the top-level Pydantic data model
    # (as specified in the *response_class*). This is used to determine when
    # temporary response data in *_response_data* is considered 'complete' for
    # a particular response ID (determined automatically).
    _required_fields: set[str]
    # A dictionary of the available localisations that can be loaded on demand
    # (determined automatically).
    _localisations_available: dict[str, str]
    # A dictionary of localisation data. Populated lazily as localisations are
    # requested.
    _localisation_data: dict[str, dict[Any, Any]]

    def __init__(self):
        """Initialise the EelTaskAPI."""
        self._task_package = self._find_parent_package()
        self._response_data = {}
        self._required_fields = self.response_class.get_required_fields()
        self._localisations_available = {}
        self._localisation_data = {}

    @classmethod
    def exception_handler(cls, exc: Exception) -> None:
        """Default exception handler for exceptions occuring during API calls.

        Handles exceptions by logging them and passing them to the frontend
        via booteel.

        Arguments:
            exc: The exception that needs to be handled.
        """
        if isinstance(exc, ValidationError):
            booteel_utils.modal(
                "Data Validation Error",
                validation_error_to_html(exc),
                icon="database-exclamation",
            )
        else:
            booteel_utils.displayexception(exc)
        cls.logger.exception(exc)

    @classmethod
    def _find_parent_package(cls) -> str:
        """Return the qualified name of the class's containing package."""
        hierarchy = cls.__module__.split(".")
        return ".".join(hierarchy[:-1])

    @classmethod
    def _cast_uuid(cls, uuid: AnyUUID) -> UUID:  # noqa: C901
        """Take a UUID in the form of `AnyUUID` and cast it to `uuid.UUID`.

        Convenience method to ensure that a uuid that is not known to be a
        `uuid.UUID` instance is cast to `uuid.UUID`, or an error raised if it
        is not a valid UUID.

        Arguments:
            uuid: A UUID in the form of either a `uuid.UUID` instance, a
                hex-string, a `bytes` sequence, an `int` or a tuple of `int`
                fields (see the `uuid.UUID` documentation for more details).

        Returns:
            Returns a `uuid.UUID` instance encapsulating the specified *uuid*
            if the UUID could be cast successfully, raises a
            `ValueError` otherwise.

        Raises:
            InvalidUUIDError: Raised if the *uuid* argument could not be cast to
                a `uuid.UUID` instance.
        """
        if isinstance(uuid, UUID):
            return uuid
        try:
            if isinstance(uuid, str):
                return UUID(uuid)
            if isinstance(uuid, bytes):
                return UUID(bytes=uuid)
            if isinstance(uuid, int):
                return UUID(int=uuid)
            if isinstance(uuid, tuple):
                return UUID(fields=uuid)
        except (AttributeError, TypeError):
            pass
        raise errors.InvalidUUIDError(
            f"Could not cast value {uuid!r} to UUID.", cls._find_parent_package()
        )

    @staticmethod
    def _find_missing_keys(d: dict[KeyT, Any], required: Iterable[KeyT]) -> set[KeyT]:
        """Find *required* keys that are missing from a dictionary *d*.

        Checks *d* for the presence of the keys in *required* and returns a
        (potentially empty) set of keys that were in *required* but that were
        not found in *d*.

        A common pattern to check for missing keys is as follows::

            required = ("name", "age", "happiness")
            if missing := self._find_missing_keys(data, required):
                self.logger.error(f"Missing keys: {missing!r}")
            else:
                print("Thanks, all required keys were supplied!")

        Arguments:
            d: The dictionary to be inspected for the *required* keys.
            required: The keys which should be present in *d*.

        Returns:
            The set of keys that were in *required* but not in *keys*.
            Empty (and therefore falsy) if all *required* keys are present
            in *d*. Non-empty (and therefore truthy) if any of the keys in
            *required* are not present in *d*.
        """
        missing = set()
        for key in required:
            if key not in d:
                missing.add(key)
        return missing

    @staticmethod
    def _cast_bools(
        d: dict[KeyT, _T], keys: Iterable[KeyT]
    ) -> tuple[dict[KeyT, _T | bool], list[KeyT]]:
        """Cast the values specified by *keys* in *d* to `bool`.

        Takes a dictionary *d* with an iterable of *keys* in *d* and attempts
        to cast the values indexed by all *keys* in *d* to `bool`.
        For casting, the following are considered truthy/falsy:
            - Truthy values: `True, "yes", "true", 1, 1.0`.
            - Falsy values: `False, "no", "false", 0, 0.0`.

        A common pattern to cast bools in a dictionary is as follows::

            booleans = ("is_happy", "speaks_english")
            data, invalid = self._cast_bools(data, booleans)
            if invalid:
                self.logger.error(
                    f"Could not cast the following keys to bool: {invalid!r}"
                )
            else:
                print(
                    f"You are {(not x)*'not '}happy and "
                    f"you {(not y)*'do not '}speak English!"
                )

        Note:
            This method does _not_ throw an exception when casting fails
            or when a specified key is not found in *d*.
            Where a value cannot be cast to `bool` according to the above rules,
            the key for the invalid field is in the *invalid* part of the return
            value.
            Keys that are missing from *d* are ignored and _not_ included in the
            *invalid* part of the returned tuple. This means that you can pass
            optional fields to the method. To detect required fields that may be
            missing from *d*, use `ResearchTaskAPI._find_missing_keys()`.

        Arguments:
            d: The dictionary whose values (specified by *keys*) should be cast
                to `bool`.
            keys: The *keys* in *d* which should be cast to `bool`.

        Returns:
            Returns a tuple of the form (*d*, *invalid*), where *d* is the
            supplied dictionary *d* with the values specified by *keys* cast to
            `bool`, and *invalid* is a (potentially empty) subset of *keys* for
            which the value could not be cast to `bool` according to the above
            rules.
        """
        invalid_fields: list[str] = []
        ACCEPTED_STRINGS = ("yes", "true", "no", "false")
        for field in keys:
            if field in d:
                if isinstance(d[field], bool):
                    pass
                elif isinstance(d[field], str) and d[field].lower() in ACCEPTED_STRINGS:
                    d[field] = True if d[field].lower() in ("yes", "true") else False
                elif isinstance(d[field], int) and d[field] in (0, 0.0, 1, 1.0):
                    d[field] = bool(d[field])
                else:
                    invalid_fields.append(field)
        return (d, invalid_fields)

    @staticmethod
    def _cast_ints(
        d: dict[KeyT, _T], keys: Iterable[KeyT]
    ) -> tuple[dict[KeyT, _T | int], list[KeyT]]:
        """Cast the values specified by *keys* in *d* to `int`.

        Takes a dictionary *d* with an iterable of *keys* in *d* and attempts
        to cast the values indexed by all *keys* in *d* to `int`.

        Note:
            This method does _not_ throw an exception when casting fails
            or when a specified key is not found in *d*.
            Where a value cannot be cast, the key for the invalid field is in
            the *invalid* part of the return value.
            Keys that are missing from *d* are ignored and _not_ included in the
            *invalid* part of the returned tuple. This means that you can pass
            optional fields to the method. To detect required fields that may be
            missing from *d*, use `ResearchTaskAPI._find_missing_keys()`.

        Arguments:
            d: The dictionary whose values (specified by *keys*) should be cast
                to `int`.
            keys: The *keys* in *d* which should be cast to `int`.

        Returns:
            Returns a tuple of the form (*d*, *invalid*), where *d* is the
            supplied dictionary *d* with the values specified by *keys* cast to
            `int`, and *invalid* is a (potentially empty) subset of *keys* for
            which the value could not be cast to `int` according to the above
            rules.
        """
        invalid_fields: list[str] = []
        for field in keys:
            if field in d:
                if isinstance(d[field], int):
                    pass
                else:
                    try:
                        d[field] = int(d[field])
                    except Exception:
                        invalid_fields.append(field)
        return (d, invalid_fields)

    @staticmethod
    def _cast_floats(
        d: dict[KeyT, _T], keys: Iterable[KeyT]
    ) -> tuple[dict[KeyT, _T | float], list[KeyT]]:
        """Cast the values specified by *keys* in *d* to `float`.

        Takes a dictionary *d* with an iterable of *keys* in *d* and attempts
        to cast the values indexed by all *keys* in *d* to `float`.

        Note:
            This method does _not_ throw an exception when casting fails
            or when a specified key is not found in *d*.
            Where a value cannot be cast, the key for the invalid field is in
            the *invalid* part of the return value.
            Keys that are missing from *d* are ignored and _not_ included in the
            *invalid* part of the returned tuple. This means that you can pass
            optional fields to the method. To detect required fields that may be
            missing from *d*, use `ResearchTaskAPI._find_missing_keys()`.

        Arguments:
            d: The dictionary whose values (specified by *keys*) should be cast
                to `float`.
            keys: The *keys* in *d* which should be cast to `float`.

        Returns:
            Returns a tuple of the form (*d*, *invalid*), where *d* is the
            supplied dictionary *d* with the values specified by *keys* cast to
            `float`, and *invalid* is a (potentially empty) subset of *keys* for
            which the value could not be cast to `float` according to the above
            rules.
        """
        invalid_fields: list[str] = []
        for field in keys:
            if field in d:
                if isinstance(d[field], float):
                    pass
                else:
                    try:
                        d[field] = float(d[field])
                    except Exception:
                        invalid_fields.append(field)
        return (d, invalid_fields)

    @EelAPI.exposed
    def response_exists(self, response_id: AnyUUID) -> bool:
        """Check whether the response with *response_id* exists."""
        response_id = self._cast_uuid(response_id)
        return response_id in self._response_data

    def _response_exists_or_raise(self, response_id: UUID):
        """Raise ResponseNotFoundError if *response_id* does not exist."""
        if response_id not in self._response_data:
            raise errors.ResponseNotFoundError(
                f"No response with id {response_id!s} found",
                self._task_package,
                response_id,
            )

    def set_location(self, location: str) -> None:
        """Set the location for the frontend to the URL *location*.

        This is a simple wrapper for `booteel.setlocation()`, provided
        on every `ResearchTaskAPI` instance for convenience so that `booteel`
        does not have to be imported specially for this very common need.

        Arguments:
            location: target URL as a string, typically a relative path.
        """
        return booteel_utils.setlocation(location)

    @EelAPI.exposed
    def get_localisations(self, force_rediscovery: bool = False) -> dict[str, str]:
        """Get a dictionary of available task localisations.

        Looks for the localisations as part of the package data in the
        :code:`localisations` subpackage of the :code:`__module__` where the
        `ReseatchTaskAPI` (or its derived subclass) was defined.

        The available localisations data is lazy-loaded and memoized, meaning
        that repeated calls are cheap and the preferred way to check for
        available localisations.

        Because of memoization, localisations added to a package after the first
        call to `ResearchTaskAPI.get_localisations()` are not detected. However,
        a full rediscovery and update of the available localisations can be
        forced by specifying the optional *force_rediscovery* argument as
        `True`.

        Note:
            The localisations themselves are not loaded simply by querying their
            availability. Localisations are individually lazy-loaded when
            `ResearchTaskAPI.load_localisation()` is first called to load a
            specific localisations.

        Arguments:
            force_rediscovery: Optional argument to indicate whether a full
                rediscovery and update of the available localisations should be
                performed irrespective of any already memoized localisation
                data. Useful mainly for on-the-fly rediscovery during debugging.
                Default: `False`.

        Returns:
            A dictionary with the localisation's label as key and its
            description as value.
        """
        if not force_rediscovery and len(self._localisations_available) > 0:
            return self._localisations_available

        self._localisations_available = dict()
        resource_target = ".".join((self._task_package, "localisations"))
        for item in resources.contents(resource_target):
            if not (
                resources.is_resource(resource_target, item)
                and item[0] not in ("_", ".")
                and item.endswith(".json")
            ):
                continue  # Not a JSON file or marked as private
            with resources.open_text(resource_target, item) as fp:
                buf = json.load(fp)
                if (
                    "meta" in buf
                    and "versionId" in buf["meta"]
                    and "versionName" in buf["meta"]
                ):
                    label, description = (
                        buf["meta"]["versionId"],
                        buf["meta"]["versionName"],
                    )
                    self._localisations_available[label] = description
                else:
                    self.logger.error(
                        f"Resource '{resource_target}/{item}' is missing one of the required keys "
                        "'meta.versionId' or 'meta.versionName'."
                    )
        return self._localisations_available

    @EelAPI.exposed
    def load_localisation(  # noqa: C901
        self,
        label_or_uuid: str | AnyUUID,
        sections: list[str] | None = None,
        force_reload: bool = False,
    ) -> dict[str, dict[str, Any]]:
        """Load the localisation indicated by *label_or_id*, if available.

        If *label_or_uuid* is a valid UUID (potentially after casting with
        `ResearchTaskAPI._cast_uuid()`), the localisation label is looked up
        from the response in progress with the matching UUID (if there is one),
        otherwise *label_or_uuid* is assumed to represent a localisation label
        such as :code:`"CymEng_Eng_GB"`.

        If *sections* is given as an argument, only the sections specified by
        the section labels in *sections* are returned. If *sections* is not
        specified, all sections from the localisation are returned.

        Each localisation is lazy-loaded and memoized the first time the
        localisation with a specific localisation label is loaded using
        `ResearchTaskAPI.load_localisation()`. All sections are
        loaded when this happens, irrespective of the value of *sections*.
        To force reloading a localisation from disk (e.g. because it was
        modified during development or debugging), the optional argument
        *force_reload* can be specified as `True`.

        Arguments:
            label_or_uuid: Either a UUID or a string specifying the label of the
                localisation to be loaded.
            sections: A list of section labels to be returned for the loaded
                localisation. Default: `None`.
            force_reload: Whether to reload the localisation from disk even if
                it has already been loaded and memoized. Useful mainly for
                on-the-fly rediscovery during debugging. Default: `False`.

        Returns:
            Returns a dictionary of the requested localisation data with section
            labels as keys as the localisation data for that section as value.
            Any requested section data that does not exist in the localisation
            file is ignored and does not raise errors - it is up to the
            recipient to check that the data for the requested section labels is
            actually present and populated.

        Raises:
            ModuleNotFoundError: If the resources package for the task is not
                found. This indicates a problem with package structure or the
                configuration of the `ResearchTaskAPI` instance.
            OSError: If the requested localisation label was found but the file
                could either not be found or not be read for some reason. May
                indicate a problem with the localisation file's name or its
                metadata.
            ValueError: Can be raised for two reasons. First, if an UUID was
                specified for *label_or_uuid* and no response with that UUID
                exists. Second, if the requested localisation file could be read
                but its contents were invalid, e.g. because they are not valid
                JSON or because they are in the wrong format or the file was
                corrupted.
        """
        # Determine localisation label
        response_id: UUID | None = None
        try:
            response_id = self._cast_uuid(label_or_uuid)
        except ValueError:
            pass

        if response_id:
            self._response_exists_or_raise(response_id)
            try:
                label = self._response_data[response_id]["meta"].task_localisation
            except KeyError as e:
                raise errors.ResponseCorruptedError(
                    f"Response with id {response_id!s} is missing the 'meta' key",
                    task=self._task_package,
                    response_id=response_id,
                ) from e
            except AttributeError as e:
                raise errors.ResponseCorruptedError(
                    (
                        f"Response with id {response_id!s} is missing"
                        "the 'meta.task_localisaton' attribute"
                    ),
                    task=self._task_package,
                    response_id=response_id,
                ) from e
        else:
            label = label_or_uuid

        # Lazy-load localisation data if needed
        if force_reload or label not in self._localisation_data:
            resource_target = ".".join((self._task_package, "localisations"))
            try:
                if force_reload or not self._localisations_available:
                    self.get_localisations(force_rediscovery=force_reload)
                self._localisations_available[
                    label
                ]  # Raise KeyError if label not found
                buffer = None
                with resources.open_text(resource_target, f"{label}.json") as fp:
                    buffer = json.load(fp)
                assert isinstance(buffer, dict)
                self._localisation_data[label] = buffer
                self.logger.debug(
                    f"Successfully hard-loaded localisation {label} data for "
                    f"{self.__class__.__name__} from package {resource_target}."
                )
            except ModuleNotFoundError as e:
                raise errors.ResourceError(
                    f"The package {resource_target!r} was not found: {e.msg}",
                    task=self._task_package,
                ) from e
            except OSError as e:
                raise errors.ResourceError(
                    (
                        "An error occured while trying to access the resource "
                        f"'{resource_target!s}.{label!s}.json' for reading: {e!s}"
                    ),
                    task=self._task_package,
                ) from e
            except KeyError as e:
                raise errors.ResourceError(
                    (
                        "Could not hard-load localisation "
                        f"'{resource_target!s}.{label!s}': unknown localisation label"
                    ),
                    task=self._task_package,
                ) from e
            except (json.JSONDecodeError, AssertionError) as e:
                msg = e.msg if isinstance(e, json.JSONDecodeError) else "invalid format"
                raise errors.ResourceError(
                    (
                        "Could not hard-load localisation "
                        f"'{resource_target!s}.{label!s}': {msg}"
                    ),
                    task=self._task_package,
                ) from e

        # Return appropriate sections of localisation data
        if sections is None:
            return self._localisation_data[label]
        buffer: dict[str, dict[str, Any]] = {}
        for section in sections:
            if section in self._localisation_data[label]:
                buffer[section] = self._localisation_data[label][section]
        return buffer

    @EelAPI.exposed
    def new(self, data: dict[str, Any]) -> str:
        """Initialise a new Task response.

        The *data* argument must be a dictionary containing at least the
        following keys:
            * `selectSurveyVersion`
            * `researcherId`
            * `participantId`
            * `confirmConsent`

        Arguments:
            data: A dictionary of response data.

        Returns:
            On success, returns the UUID of the new response as a hex-string.
        """
        self.logger.info(f"Creating new {self.__class__.__name__} response..")
        response_id = uuid1()
        self.logger.info(f"... response_id={response_id}")
        self.logger.debug(f"... data={data!r}")
        required = (
            "selectSurveyVersion",
            "researcherId",
            "participantId",
            "confirmConsent",
        )
        if missing := self._find_missing_keys(data, required):
            raise errors.MissingKeysError(
                (
                    f"Failed to create new {self._task_package} response: "
                    f"missing keys {missing!r}."
                ),
                task=self._task_package,
                missing_keys=missing,
                response_id=response_id,
            )
        meta = ResponseMetadata(
            task_localisation=data["selectSurveyVersion"],
            task_version_no=self.task_version,
            app_version_no=config.appversion,
            app_system_useragent="Unknown",  # @TODO
            app_display_language="en_GB",  # @TODO
            researcher_id=data["researcherId"],
            research_location=data["researchLocation"],
            participant_id=data["participantId"],
            consent_obtained=data["confirmConsent"],
        )
        self.logger.debug(f"... meta={meta!r}")
        self._response_data[response_id] = {}
        self._response_data[response_id]["id"] = response_id
        self._response_data[response_id]["meta"] = meta
        self.logger.debug("... success.")
        self.set_location(f"start.html?instance={response_id!s}")
        return str(response_id)

    @EelAPI.exposed
    def discard(self, response_id: AnyUUID) -> Literal[True] | None:
        """Discard all data for response with id *response_id*.

        Arguments:
            response_id: UUID of the response to discard.

        Returns:
            `True` if successful. An exception is raised if unsuccessful.

        Raises:
            ResponseNotFoundError: Raised if the response to be discarded does
                not exist.
        """
        response_id = self._cast_uuid(response_id)
        self._response_exists_or_raise(response_id)
        self.logger.info(
            f"Discarding {self.__class__.__name__} response with id {response_id}.."
        )
        del self._response_data[response_id]
        self.logger.debug("... success.")
        return True

    @EelAPI.exposed
    def is_complete(self, response_id: AnyUUID) -> bool:
        """Check whether response with id *response_id* is complete.

        Arguments:
            response_id: UUID of the response to check.

        Returns:
            `True` if all the required fields for the response are present,
            `False` if at least one required field is still missing.

        Raises:
            ResponseNotFoundError: Raised if no response with *response_id* is found.
            ResponseStorageError: Raised if the response data cannot be written to file.
        """
        response_id = self._cast_uuid(response_id)
        self._response_exists_or_raise(response_id)
        self.logger.info(
            f"Check completeness of {self.__class__.__name__} response with id {response_id}.."
        )
        for field in self._required_fields:
            if field not in self._response_data[response_id]:
                self.logger.info(
                    f"... response is incomplete - missing {field} (possibly more)."
                )
                return False
        self.logger.info("... response is complete.")
        return True

    @EelAPI.exposed
    def store(self, response_id: AnyUUID) -> Literal[True] | None:
        """Submit a complete response to long-term storage."""
        response_id = self._cast_uuid(response_id)
        self._response_exists_or_raise(response_id)
        self.logger.info(
            f"Storing data for {self.__class__.__name__} response with id {response_id}.."
        )
        response = self.response_class(**self._response_data[response_id])
        json = response.json(indent=4)
        self.logger.debug(f"... JSON serialization: {json}")
        path = self.task_data_path / str(response.meta.task_localisation)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        filename = path / f"{response.meta.participant_id!s}_{response_id!s}.json"
        self.logger.debug(f"... writing to file: {filename}")
        try:
            with filename.open("w") as fp:
                fp.write(json)
        except OSError as e:
            self.logger.debug("... failed.")
            raise errors.ResponseStorageError(
                f"Could not store response with id {response_id}: {e!s}",
                task=self._task_package,
                response_id=response_id,
            ) from e
        self.logger.debug("... success.")
        return True

    @EelAPI.exposed
    def end(self, response_id: AnyUUID, data: dict[str, Any] | None = None) -> str:
        """Redirect participant to next task in sequence and remove current response from memory.

        Important:
            Response data for *response_id* is discarded from memory once :func:`end()` is called.
            You **must** call :func:`store()` before calling :func:`end()` to store the data.
        """
        response_id = self._cast_uuid(response_id)
        self._response_exists_or_raise(response_id)
        self.logger.info(
            f"Redirect participant after {self.__class__.__name__} response with id {response_id}.."
        )
        if not self.is_complete(response_id):
            raise errors.ResponseIncompleteError(
                f"Cannot redirect participant: response with id {response_id} is incomplete.",
                task=self._task_package,
                response_id=response_id,
            )
        task_name = self._task_package.split(".")[-1]
        if hasattr(config.sequences, task_name):
            self.logger.debug("... sequencing information found.")
            response_meta = self._response_data[response_id]["meta"]
            query = booteel_utils.buildquery(
                {
                    "selectSurveyVersion": str(response_meta.task_localisation),
                    "researcherId": str(response_meta.researcher_id),
                    "researchLocation": str(response_meta.research_location),
                    "participantId": str(response_meta.participant_id),
                    "confirmConsent": str(int(response_meta.consent_obtained)),
                    "surveyDataForm.submit": "true",
                }
            )
            href = f"/app/{getattr(config.sequences, task_name)}/index.html?{query}"
            self.logger.debug(f"... redirecting to: {href}")
            self.set_location(href)
        else:
            href = "/app/index.html"
            self.logger.debug(f"... no sequencing information for {task_name!r} found.")
            self.logger.debug(f"... redirecting to: {href}")
            self.set_location(href)
        self.discard(response_id)
        return href
