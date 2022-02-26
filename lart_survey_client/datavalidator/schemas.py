"""Prototypes to conveniently define data classes with built-in validation."""
from typing import Union, Optional, Any, Callable
import re

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


class DataField:
    """Base class for data schema fields.

    To instantiate, use VField, CField, or shorthand notation in a DataSchema
    declaration.
    """

    def __init__(self, name: str, type_: Any, typedesc: str, required: bool = True):
        """Instantiates a new DataField."""
        self.name: str = name
        self.type_: Any = type_
        self.typedesc: str = typedesc
        self.required: bool = required

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

    def __init__(
        self,
        name: str,
        type_: str,
        typedesc: str,
        vmethod: Union[str, Callable[[Any], Any]],
        required: bool = True,
    ):
        """Instantiates a new CField."""
        super().__init__(name, type_, typedesc, required)
        self.vmethod: Union[str, Callable[[Any], Any]] = vmethod

    def __repr__(self) -> str:
        """Returns a Pythonesque string representation of the CField."""
        label = self.__class__.__name__
        params = {
            "name": repr(self.name),
            "type_": repr(self.type_),
            "typedesc": repr(self.typedesc),
            "vmethod": repr(self.vmethod),
            "required": repr(self.required),
        }
        paramspec = ", ".join(f"{k}={v}" for k, v in params.items())
        return f"{label}({paramspec})"


class VField(DataField):
    """Defines an auto-validated data field for DataSchema classes."""

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


class DataSchema:
    """Abstract base class to define auto-validating data classes.
    
    @TODO:  - __getattr__(self, name) - to retreive data
            - __setattr__(self, name, value) - to set data (with validation)
            - __delattr__(self, name) - to remove/clear a datapoint
            - Move some __new__ stuff to __init_subclass__(cls)?
            - Functions to set and validate data by group (inject to getattr()?)
            - JSON import/export
    """

    __schematized: bool
    __data: SchemaDataT

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
            cls.__schematized = True
        self = super().__new__(cls)
        privateref = f"_{cls.__name__}__data"
        if not hasattr(self, privateref):
            setattr(self, privateref, self.__materialize())
            self.__data = getattr(self, privateref)
        return self

    def iscomplete(self, onlyrequired: bool = True) -> bool:
        """Checks whether the dataset is complete."""
        return not bool(self.getmissing(onlyrequired))

    def getmissing(self, onlyrequired: bool = True) -> SchemaDataT:  # noqa: C901
        """Return a schematic dict with field schemas for missing fields.

        @BUG: Should check for DataFieldList instances not just whether the name
        is there or not, but also whether the list is empty or not.
        """
        missing: SchemaDataT = {}
        for field in self.__schema.values():
            if isinstance(field, DataField) and field.name not in self.__data:
                if not onlyrequired or field.required:
                    missing[field.name] = field
            if isinstance(field, DataGroup):
                for subfield in field.fields.values():
                    if (
                        isinstance(subfield, DataField)
                        and subfield.name not in self.__data[field.name]
                    ):
                        if not onlyrequired or subfield.required:
                            if field.name not in missing:
                                missing[field.name] = {}
                            missing[field.name][subfield.name] = subfield
        return missing

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
            # It should be a VField
            return VField(schemaname, **schema)
        if {"type_", "typedesc", "vmethod"} <= keys:
            # It should be a CField
            return CField(schemaname, **schema)
        if {"type_", "typedesc"} <= keys:
            # A possible vanilla DataField
            return DataField(schemaname, **schema)
        raise TypeError("Cannot determine field type in DataScheme definition.")

    @classmethod
    def __materialize(cls) -> SchemaDataT:
        """Creates an empty __data store pre-populated with DataGroups/DataFieldLists."""
        data: SchemaDataT = {}
        for field in cls.__schema.values():
            if isinstance(field, DataGroup):
                data[field.name] = {}
                for subfield in field.fields.values():
                    if isinstance(subfield, DataFieldList):
                        data[field.name][subfield.name] = []
            elif isinstance(field, DataFieldList):
                data[field.name] = []
        return data
