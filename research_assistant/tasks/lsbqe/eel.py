"""API to exposes the LSBQe to Python Eel."""
import logging
from uuid import UUID
from typing import Any, Iterable
from ...task_api import ResearchTaskAPI
from ...config import config
from .datamodel import LsbqeTaskResponse, LsbqeTaskLsb, LsbqeTaskResidency

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
        for key, value in data.copy().items():
            if key.startswith("residencies-"):
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
                    f"residencies-{i}-name",
                    f"residencies-{i}-from",
                    f"residencies-{i}-to"
                )
                missing = self._find_missing_keys(data, required_fields)
                if missing:
                    exc = KeyError(
                        f"Failed to add ratings to {self.__class__.__name__} response: "
                        f"missing key(s): {missing!s} for LSB response."
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
                del data[key]
                del data[f"residencies-{i}-from"]
                del data[f"residencies-{i}-to"]
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
        # Supply defaults for father/mother NA
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
                "father_occupation",
                "father_other_languages"
            ))
        if not data["mother_not_applicable"]:
            required_fields.extend((
                "mother_education_level",
                "mother_occupation",
                "mother_first_language",
                "mother_second_language",
                "mother_occupation",
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
        # ...
        from pprint import pprint
        pprint(data)

        _sample_data = {
            'father_education_level': '5',
            'father_first_language': 'Deutsche Gebärdensprache (DGS)',
            'father_not_applicable': False,
            'father_occupation': 'fgfdgfd',
            'father_other_languages': 'xzcvz',
            'father_second_language': 'Belgisch-französische Gebärdensprache (LSFB)',
            'languages_spoken-0-age': '0',
            'languages_spoken-0-break_months': '0',
            'languages_spoken-0-break_years': '0',
            'languages_spoken-0-name': 'Niederländisch',
            'languages_spoken-0-proficiency_speaking': '43.0022419693023',
            'languages_spoken-0-proficiency_understanding': '67.6321354984524',
            'languages_spoken-0-source': ['s'],
            'languages_spoken-0-source_other': '',
            'languages_spoken-0-usage_listening': '59.6745059952256',
            'languages_spoken-0-usage_speaking': '33.6495084913453',
            'languages_spoken-1-age': '0',
            'languages_spoken-1-break_months': '0',
            'languages_spoken-1-break_years': '0',
            'languages_spoken-1-name': 'Romanisches Lothringisch',
            'languages_spoken-1-proficiency_speaking': '37.9482804004684',
            'languages_spoken-1-proficiency_understanding': '65.3084750070345',
            'languages_spoken-1-source': ['s'],
            'languages_spoken-1-source_other': '',
            'languages_spoken-1-usage_listening': '66.7616704940502',
            'languages_spoken-1-usage_speaking': '35.6827114213359',
            'mother_education_level': '2',
            'mother_first_language': 'x',
            'mother_not_applicable': True,
            'mother_occupation': 'l;k;',
            'mother_other_languages': '',
            'mother_second_language': ''
        }


# Required so importers know which class defines the API
eel_api = LsbqeTaskAPI
