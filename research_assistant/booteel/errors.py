"""Exception types for TaskAPIs."""

from typing import Any, Iterable


class TaskAPIException(Exception):
    """Base Exception from which EelAPI exceptions are derived."""

    msg: str
    task: str

    def __init__(self, msg: str, task: str, *args: object):
        """Initialise a new EelAPIException."""
        self.msg = msg
        self.task = task
        super().__init__(msg, *args)


class InvalidUUIDError(TaskAPIException):
    """Error indicating that a UUID is invalid."""


class ResourceError(TaskAPIException):
    """Error indicating a problem with a Task or package resource."""


class ResponseException(TaskAPIException):
    """Base Exception for TaskAPIExceptions relating to Task Responses."""

    response_id: Any

    def __init__(self, msg: str, task: str, response_id: Any = None, *args: object):
        """Initialise a new ResponseException."""
        self.response_id = response_id
        super().__init__(msg, task, *args)


class ResponseNotFoundError(ResponseException):
    """Error indicating that a Task Response could not be found."""


class ResponseIncompleteError(ResponseException):
    """Error indicating that some action cannot be taken because a Task Response is incomplete."""


class ResponseCorruptedError(ResponseException):
    """Error indicating that the response's temporary data are in a corrupted state.

    Temporary response data are considered to be corrupted when the minimal required
    data or attributes are missing or are of an unexpected type. This principally
    concerns the metadata that is required for every new response that is initiated.
    """


class ResponseStorageError(ResponseException):
    """Error indicating a problem with storing or loading response data."""


class ArgumentError(ResponseException):
    """Base Exception for TaskAPIExceptions relating to API call arguments."""

    def __init__(self, msg: str, task: str, response_id: Any = None, *args: object):
        """Initialise a new ResponseException."""
        super().__init__(msg, task, response_id, *args)


class InvalidValueError(ArgumentError):
    """Error indicating that the value of an argument was not acceptable."""


class MissingKeysError(ArgumentError):
    """Error indicating that one or more required keys are missing."""

    missing_keys: list[str]

    def __init__(
        self,
        msg: str,
        task: str,
        missing_keys: Iterable[str],
        response_id: Any = None,
        *args: object
    ):
        """Initialise a new MissingKeysError."""
        self.missing_keys = list(missing_keys)
        super().__init__(msg, task, response_id, *args)
