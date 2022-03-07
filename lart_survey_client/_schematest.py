from datavalidator.schemas import DataSchema, SchemaDataT, SchemaDescT
from datavalidator import patterns
from datavalidator.exceptions import DataValidationError
from typing import Any


class ExampleSchema(DataSchema):
    """Example implementation of a DataSchema."""

    __schema: SchemaDescT = {
        "number": {
            "type_": int,
            "typedesc": "integer",
            "constraint": patterns.LIKERT_5
        },
        "words": {
            "greek": {
                "type_": str,
                "typedesc": "Greek word",
                "constraint": r"\w*",
            },
            "english": {
                "type_": str,
                "typedesc": "English word",
                "constraint": r"\w*",
                "required": False,
            }
        },
        "bools": {
            "true": {
                "type_": bool,
                "typedesc": "true boolean",
                "constraint": True,
                "required": False,
            },
            "false": {
                "type_": bool,
                "typedesc": "false boolean",
                "constraint": False,
                "required": False,
            },
            "either": {
                "type_": bool,
                "typedesc": "true or false boolean",
                "constraint": None,
                "required": False,
            },
        },
        "listicle": {
            "type_": int,
            "typedesc": "large integer",
            "constraint": (0, 1_000),
            "multiple": True,
            "required": False
        },
    }

    __data: SchemaDataT

    def __init__(self):
        super().__init__()
        pass

    def setfield(self, name: str, value: Any):
        self.__data[name] = value

    def setsubfield(self, group: str, name: str, value: Any):
        self.__data[group][name] = value

    def getschema(self):
        return self.__schema


test1 = ExampleSchema()
test1.setfield("number", 8)
print("Test 1 - Missing (onlyrequired):", repr(test1.missing()))
print(" ")

test2 = ExampleSchema()
test2.setsubfield("words", "greek", "zeta")
print("Test 2 - Missing (onlyrequired):", repr(test2.missing()))
print("Expected: ['number']")

print("Test 1 - Complete?", test1.iscomplete())
print("Expected: False")
print("Test 2 - Complete?", test2.iscomplete())
print("Expected: False")

test2.setfield("number", 0)
print("Test 2 missing (onlyrequired):", repr(test2.missing()))
print("Expected: []")
print("Test 2 missing (all):", repr(test2.missing(onlyrequired=False)))
print("Expected: ['words/english']")
print("Test 2 - Complete?", test2.iscomplete())
print("Expected: True")

test2.setnumber(5)
test2.setwords({"english": "blue", "greek": "galazio"})
test2.setbools({"true": "x", "false": [], "either": 3})

print("Test 1 - All data:", repr(test1.data(includemissing=True)))
print("Test 2 - All data:", repr(test2.data(includemissing=True)))

print("This should throw a DataValidationError:")
try:
    test2.setlisticle([817, 0, "x"])
except DataValidationError as e:
    print("Error:", e)
else:
    print("It didn't throw an error :(")
