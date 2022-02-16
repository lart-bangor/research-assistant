"""Simple data validation tools.

This module contains a set of classes providing a simple interface for data validation
and validation-based user feedback via DataValidator objects.
"""
from typing import Any, Container, Optional, Union
import json
import re

_DataRangeOptionT = Optional[
    Union[tuple[int, int], tuple[float, float], tuple[Container[Any], Container[Any]]]
]


class DataValidationResult:
    """Data validation result.

    Each DataValidationResult represents the result of a data validation attempt in a
    DataValidator. The DataValidationResult can be queried for details on the data that
    was validated, whether it passed/failed validation, what the requirements for validation
    were, etc. A DataValidatorResult will evaluate to True if the validation has succeeded
    and to False if it has failed.
    """

    isvalid: bool
    type_: Any
    typedesc: str
    pattern: Optional[str] = None
    range_: _DataRangeOptionT = None
    data: Any

    def __init__(
        self,
        isvalid: bool,
        type_: Any,
        typedesc: str,
        pattern_or_range: Union[str, _DataRangeOptionT],
        data: Any,
    ):
        """Constructs a new DataValidatorResult.

        Args:
            isvalid: Whether the validaton has succeeded or failed.
            type_: The built-in data type against which validation was carried out.
            typedesc: A short user-intelligible description of the data's type.
            pattern_or_range: A regular expression where type_ is a string,
                a 2-tuple or 2-list with inclusive (min, max) values where type_ is numeric.
            data: The data that was evaluated, as it was evaluated (i.e. after casting iff
                the DataValidator was instructed to forcecast the data).
        """
        self.isvalid = isvalid
        self.type_ = type_
        self.typedesc = typedesc
        if isinstance(pattern_or_range, tuple):
            self.range_ = (pattern_or_range[0], pattern_or_range[1])
        elif isinstance(pattern_or_range, list):
            self.range_ = (pattern_or_range[0], pattern_or_range[1])
        else:
            self.pattern = pattern_or_range
        self.data = data

    def tostring(self) -> str:
        """Returns string explanation of the data validation result."""
        polarity = "is" if self.isvalid else "is not"
        string = (
            f"`{self.data}` {polarity} a valid {self.typedesc} of type {self.type_}."
        )
        if not self.isvalid and self.pattern is not None:
            string += f" Must match pattern `{self.pattern}`."
        elif not self.isvalid and self.range_ is not None:
            string += f" Must be in range {self.range_[0]} <= x <= {self.range_[1]}."
        return string

    def tohtml(self) -> str:
        """Returns HTML formatted explanation of the data validation result."""
        if self.isvalid:
            polarity = '<span class="dv-valid">is</span>'
        else:
            polarity = '<em class="dv-notvalid">is not</em>'
        html = f'<code class="dv-data">{self.data}</code> {polarity} a valid '
        html += f'<em class="dv-typedesc">{self.typedesc}</em> of type '
        html += f'<code class="dv-type">{self.type_}</code>.'
        if not self.isvalid and self.pattern is not None:
            html += (
                f' Must match pattern <code class="dv-pattern">{self.pattern}</code>.'
            )
        elif not self.isvalid and self.range_ is not None:
            html += (
                f' Must be in range <code class="dv-range">{self.range_[0]} &#x2264; '
            )
            html += f'<i class="dv-variable">x</i> &#x2264; {self.range_[1]}</code>.'
        return html

    def tojson(self) -> str:
        """Returns a JSON representation of the data validation result."""
        data = self.data
        if not isinstance(self.data, (str, int, float, bool, type(None))):
            try:
                json.dumps(data)
            except TypeError:
                data = str(self.data)

        return json.dumps(
            {
                "isvalid": self.isvalid,
                "type": self.type_,
                "typedesc": self.typedesc,
                "pattern": self.pattern,
                "range": self.range_,
                "data": data,
            }
        )

    def __str__(self) -> str:
        """Returns a string representation of the data validation result."""
        return self.tostring()

    def __bool__(self) -> bool:
        """Returns True if the validation was successful, False otherwise."""
        return self.isvalid

    def __repr__(self) -> str:
        """Returns a python-style representation of the data validation result object."""
        pattern_or_range = self.pattern if self.pattern is not None else self.range_
        indent = "    "
        string = f"{__class__}(\n{indent}{repr(self.isvalid)},\n{indent}"
        string += f"{repr(self.type_)},\n{indent}{repr(self.typedesc)},\n"
        string += f"{indent}{repr(pattern_or_range)},"
        return string + f"\n{indent}{repr(self.data)}\n)"


class DataValidationError(Exception):
    """Exception raised when one or more data validation errors have occured."""

    errors: list[DataValidationResult]
    message: str

    def __init__(self, message: str, errors: list[DataValidationResult]):
        """Constructs a new DataValidationError exception.

        Args:
            message: The message to be shown to the user.
            errors: A list of the DataValidationResults that have failed validation.
        """
        self.errors = errors
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        """Returns a string representation of the exception."""
        return f"{__class__}('{self.message}')"

    def __repr__(self) -> str:
        """Returns a python-stye representation of the exception."""
        return f"{__class__}({repr(self.message)}, {repr(self.errors)})"


class DataValidator:
    """Data validation interface.

    A DataValidator offers a convenient interface for validating a set of data points,
    of the same or different types. The DataValidator will store any failed validation
    results, can optionally force casting of the data to a specific type, can be evaluated
    for success in a boolean expression, and allows for the conditional raising of a
    DataValidationError exception if any validation attempts have failed.

    A single DataValidator should only be used once for a closed set of data, as reuse
    will add the results to the existing DataValidator and always evaluate False if it has
    previously had unsuccessful validation attempts (though under some circumstances, e.g.
    the successive building of datasets with late repairs, this may be desirable).
    """

    results: list[DataValidationResult] = []
    errors: list[DataValidationResult] = []
    forcecast: bool

    def __init__(self, forcecast: bool = False):
        """Constructs a new DataValidator.

        Args:
            forcecast: Whether to force casting of the data arguments to the validation
                methods to the indicated type (e.g. str for .validatestring()). This
                will set the default behaviour for validation calls, but can be overwritten
                by passing the named argument forcecast=True or forcecast=False on
                individual method calls.
        """
        self.forcecast = forcecast

    def __shouldforcecast(self, overwrite: Optional[bool] = None):
        if overwrite is not None:
            return overwrite
        return self.forcecast

    def __storeresult(self, result: DataValidationResult):
        self.results.append(result)
        if not result:
            self.errors.append(result)

    def validatestring(
        self, typedesc: str, pattern: str, data: Any, forcecast: Optional[bool] = None
    ):
        r"""Validates a string against a regular expression pattern.

        Args:
            typedesc: An end-user intelligible description of the desired data type, e.g.
                "User ID" or "postcode".
            pattern: A regular expression to match the string against. Important: Note that
                the regular expression will implicitly be enclosed by \A and \Z to match
                the beginning and end of the string. These thus need not be specified in the
                pattern provided.
            data: The data to be validated.
            forcecast: Optional argument to overwrite the objects default setting for forced
                casting of data arguments.
        """
        if self.__shouldforcecast(forcecast):
            data = str(data)
        validation = DataValidationResult(
            bool(re.match(r"\A" + pattern + r"\Z", data)), str, typedesc, pattern, data
        )
        self.__storeresult(validation)
        return validation

    def validateint(
        self,
        typedesc: str,
        range_: Union[tuple[int, int], list[int]],
        data: Any,
        forcecast: Optional[bool] = None,
    ):
        r"""Validates an integer against a regular expression pattern.

        Args:
            typedesc: An end-user intelligible description of the desired data type, e.g.
                "User ID" or "postcode".
            range_: A two member tuple or list of integers where the first element represents
                the inclusive lower bound and the second member the inclusive upper bound of
                the permissible range of integer values. For example, (3, 5) would successfully
                validate the data inputs 3, 4, 5, but fail validation for 2 or 6.
            data: The data to be validated.
            forcecast: Optional argument to overwrite the objects default setting for forced
                casting of data arguments.
        """
        if self.__shouldforcecast(forcecast):
            data = int(data)
        validation = DataValidationResult(
            (range_[0] <= data <= range_[1]), int, typedesc, tuple(range_), data
        )
        self.__storeresult(validation)
        return validation

    def validatefloat(
        self,
        typedesc: str,
        range_: Union[tuple[float, float], list[float]],
        data: Any,
        forcecast: Optional[bool] = None,
    ):
        r"""Validates a float against a regular expression pattern.

        Args:
            typedesc: An end-user intelligible description of the desired data type, e.g.
                "User ID" or "postcode".
            range_: A two member tuple or list of integers where the first element represents
                the inclusive lower bound and the second member the inclusive upper bound of
                the permissible range of integer values. For example, (3, 5) would successfully
                validate the data inputs 3, 4, 5, but fail validation for 2 or 6.
            data: The data to be validated.
            forcecast: Optional argument to overwrite the objects default setting for forced
                casting of data arguments.
        """
        if self.__shouldforcecast(forcecast):
            data = float(data)
        validation = DataValidationResult(
            (range_[0] <= data <= range_[1]), float, typedesc, tuple(range_), data
        )
        self.__storeresult(validation)
        return validation

    def validatebool(  # noqa: C901
        self,
        typedesc: str,
        range_: Union[tuple[Container[Any], Container[Any]], list[Container[Any]]],
        data: Any,
        softcast: bool = False,
        forcecast: Optional[bool] = None,
    ):
        r"""Validates a string against a regular expression pattern.

        Args:
            typedesc: An end-user intelligible description of the desired data type, e.g.
                "User ID" or "postcode".
            range_: A two member tuple or list of containers of any type (must support
                membership testing with `in`). The first member is a container of
                acceptable truthy values, the second is a container of acceptable falsy
                values. Note that python built-in boolean types True and False are always
                validated as correct.
            data: The data to be validated.
            softcast: Convert the data into True or False if it is found in the truthy
                or falsy list of values as indicated by range_. This may often be
                preferred to forced casting with bools.
            forcecast: Optional argument to overwrite the objects default setting for
                forced casting of data arguments. Note that when casted to bool, many
                values will evaluate to True that may not be intended to do so, e.g.
                the string literal "blah" will cast to True, and so would validate
                correctly even if "blah" wasn't included in the range_ of acceptable
                non-native booleans. It may thus be useful to overwrite forcecast to
                alwys be off even when the default for other validations is to use
                forced casting. The softcast option allows the conversion of values
                found in the range_ to the respective True and False booleans instead.
        """
        isvalid = False
        if self.__shouldforcecast(forcecast):
            try:
                data = bool(data)
                isvalid = True
            except Exception:  # noqa: S110
                pass
        elif isinstance(data, bool):
            isvalid = True
        elif data in range_[0]:
            isvalid = True
            if softcast:
                data = True
        elif data in range_[1]:
            isvalid = True
            if softcast:
                data = False
        validation = DataValidationResult(isvalid, bool, typedesc, tuple(range_), data)
        self.__storeresult(validation)
        return validation

    def raiseif(self):
        """Raises a DataValidationError iff at least one validation has failed."""
        if not self:
            raise DataValidationError(str(self), self.errors)

    def tostring(self, errorsonly: bool = False):
        """Returns a line-by-line string representation of validation attempts.

        Args:
            errorsonly: Whether to include only the errors or all validation attempts.
        """
        if errorsonly:
            return "\n".join([str(e) for e in self.errors])
        return "\n".join([str(e) for e in self.results])

    def __bool__(self):
        """Returns True if no validation errors have occured so far, False otherwise."""
        return bool(self.errors)

    def __str__(self):
        """Returns a line-by-line string representation of all validation attempts."""
        return self.tostring()

    def __repr__(self):
        """Returns a python-like representation of the (empty) validator object."""
        return f"{__class__}(forcecast={self.forcecast})"
