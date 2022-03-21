"""Prototypes to conveniently define data classes with built-in validation."""
from __future__ import annotations
from typing import Union, Optional, Any, Callable
from collections import Counter
from copy import copy, deepcopy
import re
from . import ValidationResult, Validator, DataValidationError, types as dvtypes


DataFieldDescT = Union[
    "DataField",  # Fully instantiated DataField
    dict[str, Any],  # For shorthand constructor notations
]

DataGroupDataT = dict[str, DataFieldDescT]

DataGroupDescT = Union[
    "DataGroup", DataGroupDataT  # Fully instantiated DataGroup  # shorthand constructor
]

SchemaDescT = dict[str, Union[DataGroupDescT, DataFieldDescT]]

SchemaDataT = dict[str, Union[dict[str, Any], Any]]

FieldParamSpecT = list[Union[tuple[str, Any, str], tuple[str, Any, str, Any]]]


class DataField:
    """Base class for data schema fields.

    To instantiate, use VField, CField, or shorthand notation in a DataSchema
    declaration.
    """

    name: str
    type_: Any
    typedesc: str
    required: bool

    _fieldparams: FieldParamSpecT = [
        ("name", str, "The name of the DataField"),
        ("type_", Any, "The data type for the DataField"),
        ("typedesc", str, "A user-intelligible description of the data type"),
        ("required", bool, "Whether the field is required", True),
    ]

    def __init__(self, name: str, type_: Any, typedesc: str, required: bool = True):
        """Instantiates a new DataField."""
        if "/" in name:
            raise TypeError(
                "DataField and DataGroup names may not include the character `/`."
            )
        self.name = name
        self.type_ = type_
        self.typedesc = typedesc
        self.required = required

    @classmethod
    def fieldparams(cls) -> FieldParamSpecT:
        """Returns the parameter list for a DataField of this type."""
        return deepcopy(cls._fieldparams)

    def fieldspecs(self) -> dict[str, Any]:
        """Returns the values for each parameter of the DataField."""
        specs: dict[str, Any] = {"fieldtype": self.__class__}
        for param in self._fieldparams:
            specs[param[0]] = getattr(self, param[0])
        return specs

    def __str__(self) -> str:
        """Returns a (possibly shortened) string representaiton of the DataField."""
        label = self.__class__.__name__
        return (
            f"{label}({repr(self.name)}, {self.type_}, "
            f"{repr(self.typedesc)}, required={self.required})"
        )

    def __repr__(self) -> str:
        """Returns a Pythonesque string representation of the DataField."""
        return self.__str__()


class CField(DataField):
    """Defines a manually validated data field for DataSchema classes."""

    vmethod: Union[str, Callable[[Any, Any], Any]]
    forcecast: Optional[bool]

    _fieldparams: FieldParamSpecT = [
        ("name", str, "The name of the DataField"),
        ("type_", Any, "The data type for the DataField"),
        ("typedesc", str, "A user-intelligible description of the data type"),
        (
            "vmethod",
            Callable[[Any, Any], Any],
            (
                "A callable accepting a two arguments: the first is the type_ of the "
                "DataField and the second the value. The callable should raise either "
                "a TypeError or a DataValidationError if the value is invalid, and "
                "must return a (possibly processed) version of the value it was passed "
                "which fits the type_ it was passed."
            ),
        ),
        (
            "forcecast",
            Optional[bool],
            "Whether to force casting of data during validation",
            None,
        ),
        ("required", bool, "Whether the field is required", True),
    ]

    def __init__(
        self,
        name: str,
        type_: str,
        typedesc: str,
        vmethod: Callable[[Any, Any], Any],
        forcecast: Optional[bool] = None,
        required: bool = True,
    ):
        """Instantiates a new CField."""
        super().__init__(name, type_, typedesc, required)
        self.vmethod = vmethod
        self.forcecast = forcecast

    def __repr__(self) -> str:
        """Returns a Pythonesque string representation of the CField."""
        label = self.__class__.__name__
        params = {
            "name": repr(self.name),
            "type_": repr(self.type_),
            "typedesc": repr(self.typedesc),
            "vmethod": repr(self.vmethod),
            "forcecast": repr(self.forcecast),
            "required": repr(self.required),
        }
        paramspec = ", ".join(f"{k}={v}" for k, v in params.items())
        return f"{label}({paramspec})"


class VField(DataField):
    """Defines an auto-validated data field for DataSchema classes."""

    constraint: Any
    forcecast: Optional[bool]
    ignorecase: Optional[bool]
    flags: Union[re.RegexFlag, int]

    _fieldparams: FieldParamSpecT = [
        ("name", str, "The name of the DataField"),
        ("type_", Any, "The data type for the DataField"),
        ("typedesc", str, "A user-intelligible description of the data type"),
        ("constraint", Any, "A DataValidator constraint approprite for type_"),
        (
            "forcecast",
            Optional[bool],
            "Whether to force casting of data during validation",
            None,
        ),
        (
            "ignorecase",
            Optional[bool],
            "Whether to ignore case for string-type data validation",
            None,
        ),
        (
            "flags",
            Union[re.RegexFlag, int],
            "Flags to pass to the regular expression engine if type_ is `str`.",
            0,
        ),
        ("required", bool, "Whether the field is required", True),
    ]

    def __init__(
        self,
        name: str,
        type_: str,
        typedesc: str,
        constraint: Any,
        forcecast: Optional[bool] = None,
        ignorecase: Optional[bool] = None,
        flags: Union[re.RegexFlag, int] = 0,
        required: bool = True,
    ):
        """Instantiates a new VField."""
        super().__init__(name, type_, typedesc, required)
        self.constraint: Any = constraint
        self.forcecast: Optional[bool] = forcecast
        self.ignorecase: Optional[bool] = ignorecase
        self.flags: Union[re.RegexFlag, int] = flags

    def __repr__(self) -> str:
        """Returns a Pythonesque string representation of the VField."""
        label = self.__class__.__name__
        params = {
            "name": repr(self.name),
            "type_": repr(self.type_),
            "typedesc": repr(self.typedesc),
            "constraint": repr(self.constraint),
            "forcecast": repr(self.forcecast),
            "ignorecase": repr(self.ignorecase),
            "flags": repr(self.flags),
            "required": repr(self.required),
        }
        paramspec = ", ".join(f"{k}={v}" for k, v in params.items())
        return f"{label}({paramspec})"


class DataFieldList(DataField):
    """Defines a field containing an arbitrary number of DataField data."""


class CFieldList(CField, DataFieldList):
    """Defines a field containing an arbitrary number of CField data."""

    pass


class VFieldList(VField, DataFieldList):
    """Defines a field containing an arbitrary number of VField data."""

    pass


class DataGroup:
    """Defines a data group for DataSchema classes."""

    def __init__(self, name: str, fields: DataGroupDataT):
        """Instantiates a new DataGroup."""
        if "/" in name:
            raise TypeError(
                "DataField and DataGroup names may not include the character `/`."
            )
        self.name: str = name
        self.fields: DataGroupDataT = fields

    def __str__(self) -> str:
        """Returns a (possibly shortened) string representaiton of the DataGroup."""
        label = self.__class__.__name__
        fieldkeys = list(self.fields.keys())
        if len(fieldkeys) > 3:
            fieldkeys = fieldkeys[:3]
            fieldkeys.append("...")
        paramspec = ", ".join(fieldkeys)
        return f"{label}(name={self.name}, fields=({paramspec}))"

    def __repr__(self) -> str:
        """Returns a Pythonesque string representation of the DataGroup."""
        label = self.__class__.__name__
        paramspec = ", ".join(f"{k}={repr(v)}" for k, v in self.fields.items())
        return f"{label}(name={self.name}, {{{paramspec}}})"

    def getfield(self, key: str) -> Union[dict[str, Any], DataField]:
        """Gets the data field with the name indicated by key."""
        if key not in self.fields:
            raise KeyError(f"Key `{key}` not found in DataGroup `{self.name}`.")
        return self.fields[key]


class DataSchema:
    """Abstract base class to define auto-validating data classes.

    @TODO:  - __getattr__(self, name) - to retreive data
            - __setattr__(self, name, value) - to set data (with validation)
            - __delattr__(self, name) - to remove/clear a datapoint
            - Move some __new__ stuff to __init_subclass__(cls)?
            - JSON import/export
    """

    forcecast: bool
    ignorecase: bool

    __schema: SchemaDescT
    __schematized: bool
    __data: SchemaDataT
    __keys: list[str]

    def __new__(cls, *args: Any, **kwargs: Any):  # noqa: C901
        """Constructs a new DataSchema instance."""
        privateref = f"_{cls.__name__}__schema"
        if not hasattr(cls, privateref):
            raise AttributeError(
                f"Instance of {cls.__name__} must define a class attribute __schema."
            )
        cls.__schema: SchemaDescT = getattr(cls, privateref)
        privateref = f"_{cls.__name__}__schematized"
        if hasattr(cls, privateref):
            cls.__schematized = getattr(cls, privateref)
        if not hasattr(cls, "__schematized") or not cls.__schematized:
            for key in cls.__schema:
                cls.__schema[key] = cls.__schematize(cls.__schema[key], key)
            cls.__keys = cls.__index()
            cls.__functionalize()
            cls.__schematized = True
        self = super().__new__(cls)
        privateref = f"_{cls.__name__}__data"
        if not hasattr(self, privateref):
            setattr(self, privateref, self.__materialize())
            self.__data = getattr(self, privateref)
        return self

    def __init__(self, forcecast: bool = True, ignorecase: bool = True):
        """Initialises a new DataSchema object."""
        self.forcecast = forcecast
        self.ignorecase = ignorecase

    @classmethod
    def __schematize(  # noqa: C901
        cls, schema: Union[DataGroupDescT, DataFieldDescT], schemaname: str
    ) -> Union[DataGroup, DataField]:
        # Is it an already instantiated DataField?
        if isinstance(schema, DataField):
            # Cannot have any subfields, so just return it..
            return schema
        # Is it an already instantiated DataGroup?
        if isinstance(schema, DataGroup):
            # Make sure each of the DataGroup's fields is instantiated
            for key in schema.fields:
                if isinstance(schema.fields[key], DataField):
                    pass
                elif isinstance(schema.fields[key], dict):
                    tmp = cls.__schematize(schema.fields[key], key)
                    if isinstance(tmp, DataGroup):
                        raise RecursionError(
                            "Not allowed to recurse in DataSchema definition."
                        )
                    schema.fields[key] = tmp
                elif isinstance(schema.fields[key], DataGroup):
                    raise RecursionError(
                        "Not allowed to recurse in DataSchema definition."
                    )
            return schema
        # Check if shorthand is a data group
        grouptype = (dict, DataGroup, DataField)  # type: ignore
        if all(isinstance(value, grouptype) for value in schema.values()):
            # We have a group of items
            fields: DataGroupDataT = {}
            for key in schema:
                tmp = cls.__schematize(schema[key], key)
                if isinstance(tmp, DataGroup):
                    raise RecursionError(
                        "Not allowed to recurse in DataSchema definition."
                    )
                fields[key] = tmp
            return DataGroup(schemaname, fields)
        keys = schema.keys()
        if {"type_", "typedesc", "constraint"} <= keys:
            # It should be a VField(List)
            if schema.pop("multiple", False):
                return VFieldList(schemaname, **schema)
            return VField(schemaname, **schema)
        if {"type_", "typedesc", "vmethod"} <= keys:
            # It should be a CField(List)
            if schema.pop("multiple", False):
                return CFieldList(schemaname, **schema)
            return CField(schemaname, **schema)
        if {"type_", "typedesc"} <= keys:
            # A possible vanilla DataField(List)
            if schema.pop("multiple", False):
                return DataFieldList(schemaname, **schema)
            return DataField(schemaname, **schema)
        raise TypeError(
            f"Cannot determine field type for `{schemaname}` in DataSchema definition."
        )

    @classmethod
    def __index(cls) -> list[str]:  # noqa: C901
        """Creates a flat list of index keys, separating groups and fields with "/"."""
        indices: list[str] = []
        groups: set[str] = set()
        for field in cls.__schema.values():
            if isinstance(field, DataGroup):
                groups.add(field.name)
                for subfield in field.fields.values():
                    if isinstance(subfield, DataField):
                        indices.append(f"{field.name}/{subfield.name}")
            elif isinstance(field, DataField):
                indices.append(field.name)
        if len(set(indices)) != len(indices) or not groups.isdisjoint(indices):
            message: list[str] = []
            duplicates: list[str] = [k for k, v in Counter(indices).items() if v > 1]
            if duplicates:
                message.append("The __schema contains the following repeated keys:")
                message.append("> " + repr(duplicates))
            overlaps = groups.intersection(indices)
            if overlaps:
                message.append(
                    "The __schema contains the following overlaps "
                    "between group and field keys:"
                )
                message.append("> " + repr(overlaps))
            if not message:
                message.append("You may have found a bug...")
            raise AttributeError("\n".join(message))
        return indices

    @staticmethod
    def __setgroupfactory(
        gname: str, fieldspecs: dict[str, dict[str, Any]]
    ) -> Callable[[DataSchema, dict[str, Any]], None]:
        def setgroup(self: DataSchema, data: dict[str, Any]) -> None:
            filtered: dict[str, Any] = {}
            vr = Validator(forcecast=self.forcecast, ignorecase=self.ignorecase)
            missingfields: list[str] = []
            for key in fieldspecs:
                if key not in data and fieldspecs[key]["required"]:
                    missingfields.append(key)
            if missingfields:
                raise ValueError(
                    f"Data parameter is missing required field(s): {missingfields}."
                )
            for key, value in data.items():
                if key not in fieldspecs:
                    raise KeyError(f"The group `{gname}` has no field `{key}`.")
                fieldspec = fieldspecs[key]
                if self._isna(value) and fieldspec["required"]:
                    raise ValueError(
                        f"The field `{key}` is required but the passed value is "
                        "None, an empty list, or missing."
                    )
                else:
                    fieldtype = fieldspec["fieldtype"]
                    if fieldtype == VField:
                        filtered[key] = self._autovalidate(vr, fieldspec, value).data
                    elif fieldtype == VFieldList:
                        filtered[key] = [
                            self._autovalidate(vr, fieldspec, v).data for v in value
                        ]
                    elif fieldtype == CField:
                        filtered[key] = self._customvalidate(vr, fieldspec, value).data
                    elif fieldtype == CFieldList:
                        filtered[key] = [
                            self._customvalidate(vr, fieldspec, v).data for v in value
                        ]
                    elif fieldtype == DataField:
                        filtered[key] = value
                    elif fieldtype == DataFieldList:
                        filtered[key] = list(value)
                    else:
                        raise AttributeError(
                            f"The field `{key}` has unexpected fieldtype `{fieldtype}`."
                        )
            vr.raiseif()
            for key, value in filtered.items():
                self.__data[gname][key] = value

        setgroup.__doc__ = f"Sets data for fields in the group `{gname}`."
        setgroup.__name__ = f"set{gname}"
        return setgroup

    @staticmethod
    def __delgroupfactory(
        gname: str, fieldspecs: dict[str, dict[str, Any]]
    ) -> Callable[[DataSchema], None]:
        def delgroup(self: DataSchema) -> None:
            for fieldname, fieldspec in fieldspecs.items():
                if fieldspec["fieldtype"] in (
                    DataFieldList,
                    VFieldList,
                    CFieldList,
                ):
                    self.__data[gname][fieldname] = []
                else:
                    self.__data[gname][fieldname] = None

        delgroup.__doc__ = f"Deletes data for all fields in the group `{gname}`."
        delgroup.__name__ = f"del{gname}"
        return delgroup

    @staticmethod
    def __getgroupfactory(
        gname: str, fieldspecs: dict[str, dict[str, Any]]
    ) -> Callable[[DataSchema], dict[str, Any]]:
        def getgroup(self: DataSchema) -> dict[str, Any]:
            return copy(self.__data[gname])

        getgroup.__doc__ = f"Retrieves data for all fields in the group `{gname}`."
        getgroup.__name__ = f"get{gname}"
        return getgroup

    @staticmethod
    def __setfieldfactory(
        fieldname: str, fieldspec: dict[str, Any]
    ) -> Callable[[DataSchema, Any], None]:
        def setfield(self: DataSchema, value: Any) -> None:
            vr = Validator(forcecast=self.forcecast, ignorecase=self.ignorecase)
            if fieldspec["fieldtype"] == VField:
                data = self._autovalidate(vr, fieldspec, value).data
            elif fieldspec["fieldtype"] == CField:
                data = self._customvalidate(vr, fieldspec, value).data
            else:  # Must be plain DataField
                data = value
            vr.raiseif()
            self.__data[fieldname] = data

        setfield.__doc__ = f"Sets the value for the field `{fieldname}`."
        setfield.__name__ = f"set{fieldname}"
        return setfield

    @staticmethod
    def __delfieldfactory(
        fieldname: str, fieldspecs: dict[str, Any]
    ) -> Callable[[DataSchema], None]:
        def delfield(self: DataSchema) -> None:
            self.__data[fieldname] = None

        delfield.__doc__ = f"Deletes the value of field `{fieldname}`."
        delfield.__name__ = f"del{fieldname}"
        return delfield

    @staticmethod
    def __getfieldfactory(
        fieldname: str, fieldspecs: dict[str, Any]
    ) -> Callable[[DataSchema], Any]:
        def getfield(self: DataSchema) -> Any:
            return copy(self.__data[fieldname])

        getfield.__doc__ = f"Retrieves the value of field `{fieldname}`."
        getfield.__name__ = f"get{fieldname}"
        return getfield

    @staticmethod
    def __setfieldlistfactory(
        fieldname: str, fieldspec: dict[str, Any]
    ) -> Callable[[DataSchema, list[Any]], None]:
        def setfieldlist(self: DataSchema, values: list[Any]) -> None:
            vr = Validator(forcecast=self.forcecast, ignorecase=self.ignorecase)
            if fieldspec["fieldtype"] == VFieldList:
                data = [self._autovalidate(vr, fieldspec, v).data for v in values]
            elif fieldspec["fieldtype"] == CFieldList:
                data = [self._customvalidate(vr, fieldspec, v).data for v in values]
            else:  # Must be plain DataFieldList
                data = list(values)
            vr.raiseif()
            self.__data[fieldname] = data

        setfieldlist.__doc__ = f"Sets the values for the field list `{fieldname}`."
        setfieldlist.__name__ = f"set{fieldname}"
        return setfieldlist

    @staticmethod
    def __delfieldlistfactory(
        fieldname: str, fieldspec: dict[str, Any]
    ) -> Callable[[DataSchema], None]:
        def delfieldlist(self: DataSchema) -> None:
            self.__data[fieldname] = []

        delfieldlist.__doc__ = f"Deletes all values from field list `{fieldname}`."
        delfieldlist.__name__ = f"del{fieldname}"
        return delfieldlist

    @staticmethod
    def __getfieldlistfactory(
        fieldname: str, fieldspec: dict[str, Any]
    ) -> Callable[[DataSchema], list[Any]]:
        def getfieldlist(self: DataSchema) -> list[Any]:
            return copy(self.__data[fieldname])  # type: ignore

        getfieldlist.__doc__ = f"Retrieves all values of the field list `{fieldname}`."
        getfieldlist.__name__ = f"get{fieldname}"
        return getfieldlist

    @classmethod
    def __functionalize(cls) -> None:
        """Dynamically creates and attaches methods to get/set values."""
        groups: dict[str, list[str]] = {}
        fields: list[str] = []
        for key in cls.__keys:
            if "/" in key:
                key0, key1 = key.split("/")
                if key0 not in groups:
                    groups[key0] = []
                groups[key0].append(key1)
            else:
                fields.append(key)
        for gname in groups:
            fieldspecs: dict[str, dict[str, Any]] = cls.__getfieldspecs(gname)
            setattr(cls, f"set{gname}", DataSchema.__setgroupfactory(gname, fieldspecs))
            setattr(cls, f"del{gname}", DataSchema.__delgroupfactory(gname, fieldspecs))
            setattr(cls, f"get{gname}", DataSchema.__getgroupfactory(gname, fieldspecs))
        for field in fields:
            fieldspec = cls.__getfieldspecs(field)[field]
            if fieldspec["fieldtype"] in (VField, CField, DataField):
                setattr(
                    cls, f"set{field}", DataSchema.__setfieldfactory(field, fieldspec)
                )
                setattr(
                    cls, f"del{field}", DataSchema.__delfieldfactory(field, fieldspec)
                )
                setattr(
                    cls, f"get{field}", DataSchema.__getfieldfactory(field, fieldspec)
                )
            elif fieldspec["fieldtype"] in (VFieldList, CFieldList, DataFieldList):
                setattr(
                    cls,
                    f"set{field}",
                    DataSchema.__setfieldlistfactory(field, fieldspec),
                )
                setattr(
                    cls,
                    f"del{field}",
                    DataSchema.__getfieldlistfactory(field, fieldspec),
                )
                setattr(
                    cls,
                    f"get{field}",
                    DataSchema.__delfieldlistfactory(field, fieldspec),
                )
            else:
                raise AttributeError(
                    f"The field `{field}` has unexpected fieldtype "
                    f"`{fieldspec['fieldtype']}`."
                )

    @classmethod
    def __materialize(cls) -> SchemaDataT:  # noqa: C901
        """Creates an empty __data store pre-populated with DataGroups/DataFieldLists."""
        data: SchemaDataT = {}
        for field in cls.__schema.values():
            if isinstance(field, DataGroup):
                data[field.name] = {}
                for subfield in field.fields.values():
                    if isinstance(subfield, DataFieldList):
                        data[field.name][subfield.name] = []
                    elif isinstance(subfield, DataField):
                        data[field.name][subfield.name] = None
            elif isinstance(field, DataFieldList):
                data[field.name] = []
            elif isinstance(field, DataField):
                data[field.name] = None
        return data

    def _customvalidate(
        self, vr: Validator, fieldspec: dict[str, Any], value: Any
    ) -> ValidationResult:
        """Calls a custom validation method on value and appends result to vr."""
        if fieldspec["fieldtype"] not in (CField, CFieldList):
            raise ValueError("Fieldtype must be CField.")
        forcecast = fieldspec["forcecast"]
        if forcecast is None:
            forcecast = self.forcecast
        result = value
        if forcecast:
            try:
                result = fieldspec["type_"](result)
            except Exception:  # noqa: S110
                pass
        try:
            result = fieldspec["vmethod"](fieldspec["type_"], value)
            success = True
        except (TypeError, DataValidationError):
            success = False
        vresult = ValidationResult(
            success,
            fieldspec["type_"],
            fieldspec["typedesc"],
            fieldspec["vmethod"],
            result if forcecast else value,
            value,
            forcecast,
        )
        vr.results.append(vresult)
        if success:
            vr.successful.append(vresult)
        else:
            vr.failed.append(vresult)
        return vresult

    def _autovalidate(
        self, vr: Validator, fieldspec: dict[str, Any], value: Any
    ) -> ValidationResult:
        """Calls the appropriate validation method for fieldspec and value."""
        if fieldspec["fieldtype"] not in (VField, VFieldList):
            raise ValueError("Fieldtype must be VField.")
        forcecast = fieldspec["forcecast"]
        if forcecast is None:
            forcecast = self.forcecast
        ignorecase = fieldspec["ignorecase"]
        if ignorecase is None:
            ignorecase = self.ignorecase
        if fieldspec["type_"] == str:
            return vr.vstr(
                fieldspec["typedesc"],
                fieldspec["constraint"],
                value,
                forcecast,
                ignorecase,
                fieldspec["flags"],
            )
        if fieldspec["type_"] == int:
            return vr.vint(
                fieldspec["typedesc"], fieldspec["constraint"], value, forcecast
            )
        if fieldspec["type_"] == float:
            return vr.vfloat(
                fieldspec["typedesc"], fieldspec["constraint"], value, forcecast
            )
        if fieldspec["type_"] == bool:
            return vr.vbool(
                fieldspec["typedesc"], fieldspec["constraint"], value, forcecast
            )
        if fieldspec["type_"] == dvtypes.PolarT:
            return vr.vpolar(
                fieldspec["typedesc"],
                fieldspec["constraint"],
                value,
                forcecast,
                ignorecase,
            )
        if fieldspec["type_"] == dvtypes.EnumT:
            return vr.venum(
                fieldspec["typedesc"],
                fieldspec["constraint"],
                value,
                forcecast,
                ignorecase,
            )
        raise AttributeError(
            f"Don't know how to auto-validate field of type_ {fieldspec['type_']}. \n"
            "Permitted type_s: str, int, float, bool, PolarT, EnumT."
        )

    @classmethod
    def __getfieldspecs(cls, key: str) -> dict[str, dict[str, Any]]:
        """Get the specifications for a single DataField or fields in a DataGroup."""
        if key not in cls.__keys and key not in cls.__schema:
            raise KeyError(f"No field or group with key `{key}`.")
        if "/" in key:
            key0, key1 = key.split("/")
            field = cls.__schema[key0].fields[key1]
        else:
            field = cls.__schema[key]
        if isinstance(field, DataField):
            return {field.name: field.fieldspecs()}
        if isinstance(field, DataGroup):
            fieldspecs: dict[str, dict[str, Any]] = {}
            for subfield in field.fields.values():
                if isinstance(subfield, DataField):
                    fieldspecs[subfield.name] = subfield.fieldspecs()
                else:
                    raise AttributeError("The __schema appears to be inconsistent.")
            return fieldspecs
        raise AttributeError("The __schema appears to be inconsistent.")

    @staticmethod
    def _isna(value: Any) -> bool:
        """Returns True if value is either None or [], False otherwise."""
        if value is None or value is []:
            return True
        return False

    def _setvalue(self, key: str, value: Any) -> None:
        """Sets the value for the data addressed by key (without validation)."""
        field = self._getfield(key)
        if isinstance(field, DataFieldList) and not isinstance(value, list):
            value = list(value)
        if isinstance(field, DataField) and "/" in key:
            key0, key1 = key.split("/")
            self.__data[key0][key1] = value
        if isinstance(field, DataField) and key in self.__data:
            self.__data[key] = value
        raise KeyError(
            f"No field matching key `{key}` found in __schema (may be a group)."
        )

    def _getvalue(self, key: str) -> Any:
        """Gets the value from the data addressed by key."""
        if "/" in key:
            key0, key1 = key.split("/")
            if key0 in self.__data and key1 in self.__data[key0]:
                return self.__data[key0][key1]
        if key in self.__data:
            return self.__data[key]
        raise KeyError(
            f"No field matching key `{key}` found in __schema (may be a group)."
        )

    def _getfield(self, key: str) -> Union[DataField, DataGroup]:
        """Gets the field or group addressed by key."""
        if "/" in key:
            key0, key1 = key.split("/")
            if (
                key0 in self.__schema
                and isinstance(self.__schema[key0], DataGroup)
                and key1 in self.__schema[key0].fields
            ):
                return self.__schema[key0].fields[key1]  # type: ignore (no idea why!?)
        if key in self.__schema:
            return self.__schema[key]  # type: ignore
        raise KeyError(f"No group or field matching key `{key}` found in __schema.")

    def keys(
        self, includemissing: bool = False, onlyrequired: bool = False
    ) -> list[str]:
        """Returns a list of keys for the DataSchema."""
        return self.__keys.copy()

    def values(
        self, includemissing: bool = False, onlyrequired: bool = False
    ) -> list[Any]:
        """Returns a list of values for the data in the DataSchema."""
        values: list[Any] = []
        for key in self.__keys:
            field = self._getfield(key)
            if isinstance(field, DataField):
                value = self._getvalue(key)
                if (not self._isna(value) or includemissing) and (
                    not onlyrequired or field.required
                ):
                    values.append(value)
        return values

    def items(
        self, includemissing: bool = False, onlyrequired: bool = False
    ) -> list[tuple[str, Any]]:
        """Returns a list of key-value pairs for data in the DataSchema."""
        items: list[tuple[str, Any]] = []
        for key in self.__keys:
            field = self._getfield(key)
            if isinstance(field, DataField):
                value = self._getvalue(key)
                if (not self._isna(value) or includemissing) and (
                    not onlyrequired or field.required
                ):
                    items.append((key, value))
        return items

    def data(
        self, includemissing: bool = False, onlyrequired: bool = False
    ) -> SchemaDataT:
        """Returns the data of the DataSchema as a schematic dictionary."""
        data: SchemaDataT = {}
        for key in self.__keys:
            if "/" in key:
                key0, key1 = key.split("/")
                if key0 not in data:
                    data[key0] = {}
                field = self._getfield(key)
                value = self._getvalue(key)
                if (
                    isinstance(field, DataField)
                    and (not self._isna(value) or includemissing)
                    and (not onlyrequired or field.required)
                ):
                    data[key0][key1] = deepcopy(value)
            else:
                field = self._getfield(key)
                value = self._getvalue(key)
                if (
                    isinstance(field, DataField)
                    and (not self._isna(value) or includemissing)
                    and (not onlyrequired or field.required)
                ):
                    data[key] = deepcopy(value)
        return data

    def missing(self, onlyrequired: bool = True) -> list[str]:
        """Return a list of keys for missing fields."""
        missing: list[str] = []
        for key in self.__keys:
            field = self._getfield(key)
            if isinstance(field, DataField):
                value = self._getvalue(key)
                if self._isna(value) and (not onlyrequired or field.required):
                    missing.append(key)
        return missing

    def iscomplete(self, onlyrequired: bool = True) -> bool:
        """Checks whether the dataset is complete."""
        return not bool(self.missing(onlyrequired))
