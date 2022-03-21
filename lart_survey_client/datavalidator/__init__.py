"""Simple data validation tools.

This module contains a set of classes providing a simple interface for data validation
and validation-based user feedback via Validator objects.
"""
import json
import re
import html
from typing import Any, Callable, Union, Optional
from .types import RangeT, SetT, PolarT, PatternT, EnumT, XT, YT
from .exceptions import DataValidationError


class ValidationResult:
    """Data validation result.

    Each ValidationResult represents the result of a data validation attempt in a
    Validator. The ValidationResult can be queried for details on the data that was
    validated, whether it passed/failed validation, what the requirements for validation
    were, etc. A ValidationResult will evaluate to True if the validation has succeeded
    and to False if it has failed.
    """

    success: bool
    """Whether the data has been succeessfully validated or not."""

    type_: Any
    """The internal data type indicated for validation."""

    typedesc: str
    """A user-directed description of the type of data being validated."""

    constraint: Optional[Union[PatternT, RangeT, SetT, PolarT, PatternT, EnumT, bool]]
    """The constraint, if any, which was used to validate the data."""

    data: Any
    """The data itself, possibly cast.

    This is the data post-casting if force- or softcasting were used, and can be
    used to automatically ensure typecasting or type-narrowing for data storage.
    For the raw data pre-casting use the `raw_data` attribute.
    """

    rawdata: Any
    """The raw data, as it was passed to the validator.

    This is always the data as it was passed to the Validator, irrespective of
    whether forcecasting or softcasting were applied.
    """

    casting: bool
    """Whether the data in `data` was cast or not.

    Note that this does not necessarily mean that casting was necessary, e.g.
    an integer that was passed to a Validator's `vint()` method will still
    have been cast to int() and set the casting attribute to True despite
    being of type int before.
    """

    def __init__(
        self,
        success: bool,
        type_: Any,
        typedesc: str,
        constraint: Optional[
            Union[PatternT, RangeT, SetT, PolarT, PatternT, EnumT, bool]
        ],
        data: Any,
        rawdata: Any,
        casting: bool,
    ):
        """Constructs a new ValidationResult.

        Args:
            success: Whether the validaton has succeeded or failed.
            type_: The built-in data type against which validation was carried out.
            typedesc: A short user-intelligible description of the data's type.
            constraint: A constraint data type appropriate to the type_ of the data,
                see also the `types` submodule.
            data: The data that was evaluated (after casting if the forcecasting and/or
                softcasting options were active.)
            rawdata: The raw, uncast data as it was passed to the validation method.
            casting: Whether casting was applied to `rawdata` to yield `data`.
        """
        self.success = success
        self.type_ = type_
        self.typedesc = typedesc
        self.constraint = constraint
        self.data = data
        self.rawdata = rawdata
        self.casting = casting

    def tostring(self) -> str:
        """Returns string explanation of the data validation result."""
        polarity = "is" if self.success else "is not"
        data = self.data if self.success else self.rawdata
        string = (
            f"`{repr(data)}` {polarity} a valid {self.typedesc} of type {self.type_}."
        )
        if not self.success:
            string += f" Must match constraint: `{repr(self.constraint)}`."
        return string

    def tohtml(self) -> str:
        """Returns HTML formatted explanation of the data validation result."""
        output: list[str] = []
        output.append('<p class="dv-result">')
        data = self.data if self.success else self.rawdata
        data = html.escape(repr(data), True)
        output.append(f'<code class="dv-data">{data}</code>')
        if self.success:
            output.append('<span class="dv-success dv-successful">is</span>')
        else:
            output.append('<span class="dv-success dv-failed">is not</span>')
        output.append("a valid")
        typedesc = html.escape(self.typedesc, True)
        output.append(f'<em class="dv-typedesc">{typedesc}</em>')
        output.append("of type")
        type_ = html.escape(repr(self.type_), True)
        output.append(f'<code class="dv-type">{type_}</code>.')
        if not self.success:
            output.append("Must match constraint:")
            if isinstance(self.constraint, str):
                constraint = html.escape(self.constraint, True)
            else:
                constraint = html.escape(repr(self.constraint))
            output.append(f'<code class="dv-constraint">{constraint}</code>')
        output.append("</p>")
        return " ".join(output)

    def tojson(self) -> str:
        """Returns a JSON representation of the data validation result."""
        data = self.data
        if not isinstance(self.data, (str, int, float, bool, type(None))):
            try:
                json.dumps(data)
            except TypeError:
                data = repr(self.data)

        return json.dumps(
            {
                "isvalid": self.success,
                "type": self.type_,
                "typedesc": self.typedesc,
                "constraint": self.constraint,
                "data": data,
            }
        )

    def __str__(self) -> str:
        """Returns a string representation of the data validation result."""
        return self.tostring()

    def __bool__(self) -> bool:
        """Returns True if the validation was successful, False otherwise."""
        return self.success

    def __repr__(self) -> str:
        """Returns a python-style representation of the data validation result object."""
        indent = "    "
        string = f"{__class__.__name__}(\n{indent}{repr(self.success)},\n{indent}"
        string += f"{repr(self.type_)},\n{indent}{repr(self.typedesc)},\n"
        string += f"{indent}{repr(self.constraint)},"
        return string + f"\n{indent}{repr(self.data)}\n)"


class Validator:
    """Data validation interface.

    A Validator offers a convenient interface for validating a set of data points,
    of the same or different types. The Validator will store any failed validation
    results, can optionally force casting of the data to a specific type, can be evaluated
    for success in a boolean expression, and allows for the conditional raising of a
    DataValidationError exception if any validation attempts have failed.

    A single Validator should only be used once for a closed set of data, as reuse
    will add the results to the existing Validator and always evaluate False if it has
    previously had unsuccessful validation attempts (though under some circumstances, e.g.
    the successive building of datasets with late repairs, this may be desirable).
    """

    results: list[ValidationResult] = []
    failed: list[ValidationResult] = []
    successful: list[ValidationResult] = []
    forcecast: bool
    ignorecase: bool

    def __init__(self, forcecast: bool = False, ignorecase: bool = False):
        """Constructs a new Validator.

        Args:
            forcecast: Whether to force casting of the data arguments to the validation
                methods to the indicated type (e.g. str for .validatestring()). This
                will set the default behaviour for validation calls, but can be
                overwritten by passing the named argument forcecast=True or
                forcecast=False on individual method calls.
                For some methods, e.g. polars and enums, casting is done by passing the
                matched value rather than typecasting.
            ignorecase: Whether to ignore case in string comparisons. If true, strings
                will be compared in all uppercase, and regular expression matches will
                be passed the IGNORECASE flag. Can be overwritten on each validation call
                by passing ignorecase=True/False. Default value: False.
        """
        self.forcecast = forcecast
        self.ignorecase = ignorecase

    def __forcecast(self, overwrite: Optional[bool] = None) -> bool:
        if overwrite is not None:
            return overwrite
        return self.forcecast

    def __ignorecase(self, overwrite: Optional[bool] = None):
        if overwrite is not None:
            return overwrite
        return self.ignorecase

    def __casefolddict(self, dict_: dict[XT, YT]) -> dict[XT, YT]:
        return {self.__casefoldifstr(key): value for key, value in dict_.items()}

    def __casefoldifstr(self, x: XT) -> XT:
        if isinstance(x, str):
            return x.casefold()
        return x

    def __trycall(
        self, func: Callable[..., XT], *args: Any, **kwargs: dict[Any, Any]
    ) -> Optional[XT]:
        """Returns result of func() if possible, None if an Exception is raised."""
        try:
            return func(*args, **kwargs)
        except Exception:
            return None

    def __condcast(
        self, type_: Callable[..., XT], data: YT, overwrite: Optional[bool] = None
    ) -> Optional[Union[XT, YT]]:
        """Conditionally casts data to a type.

        Attempts to cast `data` to `type_` if, taking into account `overwrite`,
        forcecasting applies. Returns `data` itself if forcecasting doesn't apply,
        and None if forcecasting applies but `data` cannot be cast to `type_`.
        """
        if self.__forcecast(overwrite):
            return self.__trycall(type_, data)
        return data

    def __storeresult(self, result: ValidationResult):
        self.results.append(result)
        if not result:
            self.failed.append(result)
        else:
            self.successful.append(result)

    def vstr(
        self,
        typedesc: str,
        constraint: PatternT,
        data: Any,
        forcecast: Optional[bool] = None,
        ignorecase: Optional[bool] = None,
        flags: Union[re.RegexFlag, int] = 0,
    ) -> ValidationResult:
        r"""Validates a string against a regular expression pattern.

        Args:
            typedesc: An end-user intelligible description of the desired data type, e.g.
                "User ID" or "postcode".
            constraint: A regular expression to match the string against. Important: Note
                that the regular expression will implicitly be enclosed by \A and \Z to
                match the beginning and end of the string. These thus need not be
                specified in the pattern provided.
            data: The data to be validated.
            forcecast: Optional argument to overwrite the validator's default setting for
                forced casting of data arguments.
            ignorecase: Optional argument to overwrite the validator's default setting
                for case sensitivity.
            flags: Additional regex flags to be passed to re.match().
        """
        cdata = data
        try:
            if not isinstance(data, str):
                cdata = str(data)
            flags = re.IGNORECASE | flags if self.__ignorecase(ignorecase) else flags
            cmp = bool(
                re.match(r"\A{pattern}\Z".format(pattern=constraint), cdata, flags=flags)
            )
        except TypeError:
            cmp = False
        validation = ValidationResult(
            cmp,
            str,
            typedesc,
            constraint,
            self.__condcast(str, data, forcecast),
            data,
            self.__forcecast(forcecast),
        )
        self.__storeresult(validation)
        return validation

    def vint(
        self,
        typedesc: str,
        constraint: RangeT,
        data: Any,
        forcecast: Optional[bool] = None,
    ) -> ValidationResult:
        r"""Validates an integer against an inclusive range of integers or floats.

        Args:
            typedesc: An end-user intelligible description of the desired data type, e.g.
                "User ID" or "postcode".
            constraint: A two member tuple or list of integers where the first element
                represents the inclusive lower bound and the second member the inclusive
                upper bound of the permissible range of integer values. For example,
                (3, 5) would successfully validate the data inputs 3, 4, 5, but fail
                validation for 2 or 6.
            data: The data to be validated.
            forcecast: Optional argument to overwrite the validator's default setting for
                forced casting of data arguments.
        """
        cdata = data
        try:
            if not isinstance(data, int):
                cdata = int(data)
            cmp = min(constraint) <= cdata <= max(constraint)
        except (TypeError, ValueError):
            cmp = False
        validation = ValidationResult(
            cmp,
            int,
            typedesc,
            constraint,
            self.__condcast(int, data, forcecast),
            data,
            self.__forcecast(forcecast),
        )
        self.__storeresult(validation)
        return validation

    def vfloat(
        self,
        typedesc: str,
        constraint: RangeT,
        data: Any,
        forcecast: Optional[bool] = None,
    ):
        r"""Validates a float against an inclusive range of integers or floats.

        Args:
            typedesc: An end-user intelligible description of the desired data type, e.g.
                "User ID" or "postcode".
            constraint: A two member tuple or list of integers where the first element
                represents the inclusive lower bound and the second member the inclusive
                upper bound of the permissible range of integer values. For example,
                (3, 5) would successfully validate the data inputs 3, 4, 5, but fail
                validation for 2 or 6.
            data: The data to be validated.
            forcecast: Optional argument to overwrite the objects default setting for
                forced casting of data arguments.
        """
        cdata = data
        try:
            if not isinstance(data, float):
                cdata = float(data)
            cmp = min(constraint) <= cdata <= max(constraint)
        except TypeError:
            cmp = False
        validation = ValidationResult(
            cmp,
            float,
            typedesc,
            constraint,
            self.__condcast(float, data, forcecast),
            data,
            self.__forcecast(forcecast),
        )
        self.__storeresult(validation)
        return validation

    def vbool(
        self,
        typedesc: str,
        constraint: bool,
        data: Any,
        forcecast: Optional[bool] = None,
    ):
        """Validates a bool.

        Args:
            typedesc: An end-user intelligible description of the desired data type, e.g.
                "User ID" or "postcode".
            constraint: A boolean that must be matched, or None to just validate any bool.
            data: The data to be validated.
            forcecast: Optional argument to overwrite the objects default setting for
                forced casting of data arguments.
        """
        cdata = data
        try:
            if not isinstance(data, bool):
                cdata = bool(data)
            cmp = True
            if constraint is not None:
                cmp = (cdata == constraint)
        except TypeError:
            cmp = False
        validation = ValidationResult(
            cmp,
            bool,
            typedesc,
            constraint,
            self.__condcast(bool, data, forcecast),
            data,
            self.__forcecast(forcecast),
        )
        self.__storeresult(validation)
        return validation

    def vpolar(
        self,
        typedesc: str,
        constraint: PolarT,
        data: Any,
        forcecast: Optional[bool] = None,
        ignorecase: Optional[bool] = None,
    ) -> ValidationResult:
        r"""Validates a string against two sets of polar terms.

        Checkes whether data is in either of two sets of polar opposition terms. If the
        forcecast option is active, membership in the first of the two sets results in
        casting to True, membership in the second set to False, and memebership in
        neither set to None. Validation is successful if data is contained in either of
        the two sets, and unsuccessful otherwise.

        Args:
            typedesc: An end-user intelligible description of the desired data type, e.g.
                "User ID" or "postcode".
            constraint: A two member tuple or list of containers of any type (must support
                membership testing with `in`). The first member is a container of
                acceptable truthy values, the second is a container of acceptable falsy
                values. Note that python built-in boolean types True and False are always
                validated as correct.
            data: The data to be validated.
            forcecast: Optional argument to overwrite the objects default setting for
                forced casting of data arguments.
            ignorecase: Optional argument to overwrite the validator's default setting
                for case sensitivity.
        """
        cdata = data
        cval = None
        if isinstance(data, str) and self.__ignorecase(ignorecase):
            cdata = data.casefold()
            if cdata in set(map(self.__casefoldifstr, constraint[0])):
                cval = True
            elif cdata in set(map(self.__casefoldifstr, constraint[1])):
                cval = False
        else:
            if cdata in constraint[0]:
                cval = True
            elif cdata in constraint[0]:
                cval = False
            print("  Determined value:", cval)
        cmp = cval is not None
        validation = ValidationResult(
            cmp,
            PolarT,
            typedesc,
            constraint,
            cval if self.__forcecast(forcecast) else data,
            data,
            self.__forcecast(forcecast),
        )
        self.__storeresult(validation)
        return validation

    def venum(
        self,
        typedesc: str,
        constraint: EnumT,
        data: Any,
        forcecast: Optional[bool] = None,
        ignorecase: Optional[bool] = None,
    ) -> ValidationResult:
        """Validates a string against a key:value enumerable.

        Checks whether `data` is either contained in the keys or the values
        of the enumerable. If forcecasting is used, it casts to the *value*
        that was matched (not the key), or to None if no match was found.
        """
        cdata = data
        cfound = False
        cval = None
        if isinstance(data, str) and self.__ignorecase(ignorecase):
            cdata = data.casefold()
            cconst = self.__casefolddict(constraint)
            if cdata in cconst:
                cfound = True
                cval = cconst[cdata]
            elif cdata in cconst.values():
                cfound = True
                cval = cdata
        else:
            if cdata in constraint:
                cfound = True
                cval = constraint[cdata]
            elif cdata in constraint.values():
                cfound = True
                cval = cdata
        validation = ValidationResult(
            cfound,
            EnumT,
            typedesc,
            constraint,
            cval if self.__forcecast(forcecast) else data,
            data,
            self.__forcecast(forcecast),
        )
        self.__storeresult(validation)
        return validation

    def raiseif(self):
        """Raises a DataValidationError iff at least one validation has failed."""
        if bool(self.failed):
            raise DataValidationError(self.tostring(errorsonly=True), self)

    def tohtml(self, errorsonly: bool = False):
        """Returns a paragraph-by-paragraph HTML representation of validation attempts.

        Args:
            errorsonly: Whether to include only the errors or all validation attempts.
        """
        if errorsonly:
            return "\n".join(
                [f'<div class="dv-list">{e.tohtml()}</div>' for e in self.failed]
            )
        return "\n".join([f'<p class="dv-list">{e.tohtml()}</p>' for e in self.results])

    def tostring(self, errorsonly: bool = False):
        """Returns a line-by-line string representation of validation attempts.

        Args:
            errorsonly: Whether to include only the errors or all validation attempts.
        """
        if errorsonly:
            return "\n".join([str(e) for e in self.failed])
        return "\n".join([str(e) for e in self.results])

    def __bool__(self):
        """Returns True if no validation errors have occured so far, False otherwise."""
        return bool(self.failed)

    def __str__(self):
        """Returns a line-by-line string representation of all validation attempts."""
        return self.tostring()

    def __repr__(self):
        """Returns a python-like representation of the (empty) validator object."""
        return f"{__class__}(forcecast={self.forcecast})"
