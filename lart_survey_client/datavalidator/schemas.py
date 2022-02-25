"""Prototypes to conveniently define data classes with built-in validation."""
from abc import ABC, abstractmethod
from typing import Union, Optional, Any, Callable
from .types import PatternT
import re

DataFieldDescT = Union[
    "DataField",    # Fully instantiated DataField
    dict[str, Any]  # For shorthand constructor notations
]

DataGroupDescT = Union[
    "DataGroup",                                            # Fully instantiated DataGroup
    dict[str, Union[DataFieldDescT, "DataGroupDescT"]],     # shorthand constructor
    list[Union["DataField", "DataGroup"]]                   # list of full instances
]


class DataField:
    """Base class for data schema fields.

    To instantiate, use VField, CField, or shorthand notation in a DataSchema
    declaration.
    """

    def __init__(self, name: str):
        """Instantiates a new DataField."""
        self.name = name


class CField(DataField):
    """Defines a manually validated data field for DataSchema classes."""

    def __init__(
        self,
        name: str,
        type_: str,
        typedesc: str,
        validationmethod: Union[str, Callable[[Any], Any]]
    ):
        """Instantiates a new CField."""
        pass


class CFieldList(CField):
    """Defines a field containing an arbitrary number of CField data."""

    pass

class VField(DataField):
    """Defines an auto-validated data field for DataSchema classes."""

    def __init__(
        self,
        name: str,
        type_: str,
        typedesc: str,
        constraint: PatternT,
        forcecast: Optional[bool] = None,
        ignorecase: Optional[bool] = None,
        flags: Union[re.RegexFlag, int] = 0,
    ):
        """Instantiates a new VField."""
        self.name = name,
        self.type_ = type_,
        self.typedesc = typedesc,
        self.constraint = constraint,
        self.forcecast = forcecast,
        self.ignorecase = ignorecase,
        self.flags = flags


class VFieldList(VField):
    """Defines a field containing an arbitrary number of VField data."""

    pass


class DataGroup:
    """Defines a data group for DataSchema classes."""

    def __init__(
        self,
        name: str,
        fields: DataGroupDescT
    ):
        """Instantiates a new DataGroup."""
        self.name = name
        self.fields = fields


class DataSchema(ABC):
    """Abstract base class to define auto-validating data classes."""

    __schema: DataGroupDescT

    def __new__(cls, *args, **kwargs):
        """Constructs a new DataSchema instance."""
        self = super().__new__(cls)
        self.__constructschema(cls.__schema)
        return self

    @classmethod
    def __constructschema(cls, schema: DataGroupDescT) -> dict[str, Any]:
        if isinstance(schema, DataGroup):
            return cls.__constructschema(schema.fields)
        if isinstance(schema, dict):
            data = {}
            for name, definition in schema.items():
                if isinstance(definition, (dict, DataField, DataGroup)):
                    pass
        return data
