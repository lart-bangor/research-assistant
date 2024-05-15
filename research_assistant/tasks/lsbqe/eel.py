"""API to exposes the LSBQe to Python Eel."""
import logging
from uuid import UUID
from typing import Any, Iterable
from ...task_api import ResearchTaskAPI
from ...config import config
from .datamodel import LsbqeTaskResponse, LsbqeTaskLsb, LsbqeTaskLdb, LsbqeTaskResidency, LsbqeParentInformation, LsbqeLanguageSpoken

logger = logging.getLogger(__name__)


class LsbqeTaskAPI(ResearchTaskAPI):
    """Eel API for the LSBQe Task."""

    logger = logger
    response_class = LsbqeTaskResponse
    task_version = "0.5.0a0"
    task_data_path = config.paths.data / "LSBQe"
    eel_namespace = "lsbqe"

    def _make_bools(self, target_fields: Iterable[str], data: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
        invalid_fields: list[str] = []
        for field in target_fields:
            if field in data:
                if isinstance(data[field], bool):
                    pass
                elif isinstance(data[field], str) and data[field].lower() in ("yes", "true", "no", "false"):
                    data[field] = True if data[field].lower() in ("yes", "true") else False
                elif isinstance(data[field], int) and data[field] in (0, 1):
                    data[field] = bool(data[field])
                else:
                    invalid_fields.append(field)
        return (data, invalid_fields)

    @ResearchTaskAPI.exposed
    def add_lsb(self, response_id: str | UUID, data: dict[str, Any]) -> None:
        """Add LSB data to the response with id *response_id*."""
        response_id = self._cast_uuid(response_id)
        self.logger.info(
            f"Adding LSB data for {self.__class__.__name__} response with id {response_id}.."
        )
        if response_id not in self._response_data:
            exc = ValueError(
                f"Failed to add LSB data to {self.__class__.__name__} response with id "
                f"{response_id}: no response with this id in progress."
            )
            self.logger.error(str(exc))
            raise exc
        self.logger.debug(f"... lsb data: {data}")
        # Make booleans
        data, invalid_bools = self._make_bools(
            (
                "vision_impairment", "vision_aid", "vision_fully_corrected",
                "hearing_impairment", "hearing_aid"
            ),
            data
        )
        if invalid_bools:
            exc = ValueError(
                f"Failed to add LSB data to {self.__class__.__name__} response: "
                "one or more boolean fields for the LSB response contain "
                f"values other than ('yes', 'no', 'true', 'false', 0, 1): {invalid_bools!s}."
            )
            self.logger.error(exc)
            raise exc
        # Check for missing required fields
        required_fields = [
            "sex", "occupation", "handedness", "date_of_birth", "hearing_impairment",
            "vision_impairment", "place_of_birth", "education_level"
        ]
        if "sex" in data and data["sex"] == "o":
            required_fields.append("sex_other")
        if "hearing_impariment" in data and data["hearing_impairment"]:
            required_fields.append("hearing_aid")
        if "vision_impairment" in data and data["vision_impairment"]:
            required_fields.append("vision_aid")
        if "vision_aid" in data and data["vision_aid"]:
            required_fields.append("vision_fully_corrected")
        missing = self._find_missing_keys(data, required_fields)
        if missing:
            exc = KeyError(
                f"Failed to add LSB data to {self.__class__.__name__} response: "
                f"missing key(s): {missing!s} for LSB response."
            )
            self.logger.error(str(exc))
            raise exc
        # Extract residencies
        residencies_d: dict[int, tuple[str, str, str]] = dict()
        for key in data.keys():
            if key.startswith("residencies-") and key.endswith("-name"):
                try:
                    i = key.split("-")[1]
                    int(i)
                except IndexError:
                    exc = KeyError(
                        f"Failed to add LSB data to {self.__class__.__name__} response: "
                        f"invalid, non-indexed key '{key}' for residencies field on LSB response."
                    )
                    self.logger.error(str(exc))
                    raise exc
                except ValueError:
                    exc = KeyError(
                        f"Failed to add LSB data to {self.__class__.__name__} response: "
                        f"invalid, non-integer index '{i}' for residencies field on LSB response."
                    )
                    self.logger.error(str(exc))
                    raise exc
                required_fields = (
                    f"residencies-{i}-from",
                    f"residencies-{i}-to",
                )
                missing = self._find_missing_keys(data, required_fields)
                if missing:
                    exc = KeyError(
                        f"Failed to add resiency data to {self.__class__.__name__} response: "
                        f"missing key(s): {missing!s} for LSB response."
                        f"\nDATA:\n"
                        f"{data!r}"
                    )
                    self.logger.error(str(exc))
                    raise exc
                if (data[key].strip()
                        and data[f"residencies-{i}-from"].strip()
                        and data[f"residencies-{i}-to"].strip()):
                    # Only add if it's not actually an empty row
                    residencies_d[int(i)] = (
                        data[key],
                        data[f"residencies-{i}-from"] + "-01",
                        data[f"residencies-{i}-to"] + "-01"
                    )
        residencies = []
        for _, (_location, _start, _end) in sorted(residencies_d.items()):
            residencies.append(LsbqeTaskResidency(location=_location, start=_start, end=_end))
        # Remove dependent fields that ought to be left blank based on given answers
        if data["sex_other"] and data["sex"].lower() in ("m", "f"):
            data["sex_other"] = None
        if "hearing_aid" in data and not data["hearing_impairment"]:
            del data["hearing_aid"]
        if not data["vision_impairment"]:
            if "vision_aid" in data:
                del data["vision_aid"]
            if "vision_fully_corrected" in data:
                del data["vision_fully_corrected"]
        if "vision_fully_corrected" in data and "vision_aid" in data and not data["vision_aid"]:
            del data["vision_fully_corrected"]
        self.logger.debug(f"... cleaned data: {data}")
        # Construct the LSB response object
        lsb = LsbqeTaskLsb(
            sex=data["sex"],
            sex_other=(data["sex_other"] if data["sex_other"] else None),
            occupation=data["occupation"],
            handedness=data["handedness"],
            date_of_birth=data["date_of_birth"],
            hearing_impairment=data["hearing_impairment"],
            hearing_aid=(data["hearing_aid"] if "hearing_aid" in data else None),
            vision_impairment=data["vision_impairment"],
            vision_aid=(data["vision_aid"] if "vision_aid" in data else None),
            vision_fully_corrected=(data["vision_fully_corrected"] if "vision_fully_corrected" in data else None),
            place_of_birth=data["place_of_birth"],
            residencies=residencies,
            education_level=data["education_level"]
        )
        self._response_data[response_id]["lsb"] = lsb
        self.set_location(f"ldb.html?instance={response_id}")

    @ResearchTaskAPI.exposed
    def add_ldb(self, response_id: str | UUID, data: dict[str, Any]) -> None:
        """Add LDB data to the response with id *response_id*."""
        response_id = self._cast_uuid(response_id)
        self.logger.info(
            f"Adding LDB data for {self.__class__.__name__} response with id {response_id}.."
        )
        if response_id not in self._response_data:
            exc = ValueError(
                f"Failed to add LDB data to {self.__class__.__name__} response with id "
                f"{response_id}: no response with this id in progress."
            )
            self.logger.error(str(exc))
            raise exc
        self.logger.debug(f"... ldb data: {data}")
        # Make booleans
        data, invalid_bools = self._make_bools(
            ("father_not_applicable", "mother_not_applicable"),
            data
        )
        if invalid_bools:
            exc = ValueError(
                f"Failed to add LDB data to {self.__class__.__name__} response: "
                "one or more boolean fields for the LDB response contain "
                f"values other than ('yes', 'no', 'true', 'false', 0, 1): {invalid_bools!s}"
            )
            self.logger.error(exc)
            raise exc
        # Supply defaults for father/mother_not_applicable
        if "father_not_applicable" not in data:
            data["father_not_applicable"] = False
        if "mother_not_applicable" not in data:
            data["mother_not_applicable"] = False
        # Check for missing required fields
        required_fields = []
        if not data["father_not_applicable"]:
            required_fields.extend((
                "father_education_level",
                "father_occupation",
                "father_first_language",
                "father_second_language",
                "father_other_languages"
            ))
        if not data["mother_not_applicable"]:
            required_fields.extend((
                "mother_education_level",
                "mother_occupation",
                "mother_first_language",
                "mother_second_language",
                "mother_other_languages"
            ))
        missing = self._find_missing_keys(data, required_fields)
        if missing:
            exc = KeyError(
                f"Failed to add LDB data to {self.__class__.__name__} response: "
                f"missing key(s): {missing!s} for LDB response."
            )
            self.logger.error(str(exc))
            raise exc
        # Prepare parental information
        parent_info: list[LsbqeParentInformation] = []
        if not data["father_not_applicable"]:
            father = LsbqeParentInformation(
                parent="father",
                occupation=data["father_occupation"],
                first_language=data["father_first_language"],
                second_language=data["father_second_language"].strip() or None,
                other_languages=data["father_other_languages"].strip() or None
            )
            parent_info.append(father)
        if not data["mother_not_applicable"]:
            mother = LsbqeParentInformation(
                parent="mother",
                occupation=data["mother_occupation"],
                first_language=data["mother_first_language"],
                second_language=data["mother_second_language"].strip() or None,
                other_languages=data["mother_other_languages"].strip() or None
            )
            parent_info.append(mother)
        # Extract languages_spoken-X data
        languages_spoken: list[LsbqeLanguageSpoken] = []
        for key in data.keys():
            if key.startswith("languages_spoken-") and key.endswith("-name"):
                try:
                    i = key.split("-")[1]
                    int(i)
                except IndexError:
                    exc = KeyError(
                        f"Failed to add LDB data to {self.__class__.__name__} response: "
                        f"invalid, non-indexed key '{key}' for languages_spoken field on LDB response."
                    )
                    self.logger.error(str(exc))
                    raise exc
                except ValueError:
                    exc = KeyError(
                        f"Failed to add LDB data to {self.__class__.__name__} response: "
                        f"invalid, non-integer index '{i}' for languages_spoken field on LDB response."
                    )
                    self.logger.error(str(exc))
                    raise exc
                required_fields = [
                    f"languages_spoken-{i}-source",
                    f"languages_spoken-{i}-age",
                    f"languages_spoken-{i}-break_years",
                    f"languages_spoken-{i}-break_months",
                    f"languages_spoken-{i}-proficiency_speaking",
                    f"languages_spoken-{i}-proficiency_understanding",
                    f"languages_spoken-{i}-usage_listening",
                    f"languages_spoken-{i}-usage_speaking",
                ]
                if f"languages_spoken-{i}-source" in data and "o" in data[f"languages_spoken-{i}-source"]:
                    required_fields.append(f"languages_spoken-{i}-source_other")
                missing = self._find_missing_keys(data, required_fields)
                if missing:
                    exc = KeyError(
                        f"Failed to add LDB data to {self.__class__.__name__} response: "
                        f"missing key(s): {missing!s} for LDB response."
                    )
                    self.logger.error(str(exc))
                    raise exc
                source_other = None
                if "o" in data[f"languages_spoken-{i}-source"]:
                    source_other = data[f"languages_spoken-{i}-source_other"].strip()
                    if not source_other:
                        exc = ValueError(
                            f"Failed to add LDB data to {self.__class__.__name__} response: "
                            f"required field `languages_spoken-{i}-source_other` is empty."
                        )
                breaks = 0
                try:
                    breaks += int(data[f"languages_spoken-{i}-break_years"]) * 12
                    breaks += int(data[f"languages_spoken-{i}-break_months"])
                except ValueError:
                    years = data[f"languages_spoken-{i}-break_years"]
                    months = data[f"languages_spoken-{i}-break_months"]
                    exc = ValueError(
                        f"Failed to add LDB data to {self.__class__.__name__} response: "
                        f"fields `languages_spoken-{i}-break_years` and/or "
                        "`languages_spoken-{i}-break_months` contain a value that cannot "
                        f"be cast to type *int* (values: {years!r}, {months!r})."
                    )
                    self.logger.error(str(exc))
                    raise exc
                try:
                    v_speak = data[f"languages_spoken-{i}-proficiency_speaking"]
                    v_under = data[f"languages_spoken-{i}-proficiency_understanding"]
                    prof_speak = float(v_speak)
                    prof_under = float(v_under)
                    prof_read = v_read = None
                    prof_write = v_write = None
                    if f"languages_spoken-{i}-proficiency_reading" in data:
                        v_read = data[f"languages_spoken-{i}-proficiency_reading"]
                        prof_read  = float(v_read)
                    if f"languages_spoken-{i}-proficiency_writing" in data:
                        v_write = data[f"languages_spoken-{i}-proficiency_writing"]
                        prof_write  = float(v_write)
                except ValueError:
                    exc = ValueError(
                        f"Failed to add LDB data to {self.__class__.__name__} response: "
                        f"one or more of the `languages_spoken-{i}-proficiency_*` fields "
                        "contain a value that cannot be cast to type *int* "
                        f"(values: {v_speak!r}, {v_under!r}, {v_read}, {v_write})."
                    )
                    self.logger.error(str(exc))
                    raise exc
                try:
                    v_speak = data[f"languages_spoken-{i}-usage_speaking"]
                    v_listn = data[f"languages_spoken-{i}-usage_listening"]
                    usage_speak = float(v_speak)
                    usage_listn = float(v_listn)
                    usage_read = v_read = None
                    usage_write = v_write = None
                    if f"languages_spoken-{i}-usage_reading" in data:
                        v_read = data[f"languages_spoken-{i}-usage_reading"]
                        usage_read  = float(v_read)
                    if f"languages_spoken-{i}-usage_writing" in data:
                        v_write = data[f"languages_spoken-{i}-usage_writing"]
                        usage_write  = float(v_write)
                except ValueError:
                    exc = ValueError(
                        f"Failed to add LDB data to {self.__class__.__name__} response: "
                        f"one or more of the `languages_spoken-{i}-usage_*` fields "
                        "contain a value that cannot be cast to type *int* "
                        f"(values: {v_speak!r}, {v_listn!r}, {v_read}, {v_write})."
                    )
                    self.logger.error(str(exc))
                    raise exc
                language_spoken = LsbqeLanguageSpoken(
                    name=data[f"languages_spoken-{i}-name"],
                    source_home=("h" in data[f"languages_spoken-{i}-source"]),
                    source_school=("s" in data[f"languages_spoken-{i}-source"]),
                    source_community=("c" in data[f"languages_spoken-{i}-source"]),
                    source_other=source_other,
                    age=data[f"languages_spoken-{i}-age"],
                    breaks=breaks,
                    proficiency_speaking=prof_speak,
                    proficiency_understanding=prof_under,
                    proficiency_reading=prof_read,
                    proficiency_writing=prof_write,
                    usage_speaking=usage_speak,
                    usage_listening=usage_listn,
                    usage_reading=usage_read,
                    usage_writing=usage_write
                )
                languages_spoken.append(language_spoken)
        ldb = LsbqeTaskLdb(
            languages_spoken=languages_spoken,
            parents=parent_info
        )
        self._response_data[response_id]["ldb"] = ldb
        self.set_location(f"club.html?instance={response_id}")


# Required so importers know which class defines the API
eel_api = LsbqeTaskAPI
