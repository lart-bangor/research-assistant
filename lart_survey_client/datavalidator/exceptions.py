"""Exceptions for the datavalidator module."""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import Validator, ValidationResult


class DataValidationError(Exception):
    """Exception raised when one or more data validations have failed."""

    validator: "Validator"
    """The Validator object from which the DataValidationError originated."""

    errors: list["ValidationResult"]
    """The list of the ValidationResults that have failed validation."""

    message: str
    """The message to be shown to the user."""

    def __init__(self, message: str, validator: "Validator"):
        """Constructs a new DataValidationError exception.

        Args:
            message: The message to be shown to the user.
            validator: The list of the ValidationResults that have failed validation.
        """
        self.validator = validator
        self.errors = validator.failed
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        """Returns a string representation of the exception."""
        return f"{__class__.__name__}('{self.message}')"

    def __repr__(self) -> str:
        """Returns a python-stye representation of the exception."""
        return f"{__class__.__name__}({repr(self.message)}, {repr(self.errors)})"
