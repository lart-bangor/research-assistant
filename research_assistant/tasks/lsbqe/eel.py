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
                if isinstance(data[field], str) and data[field].lower() in ("yes", "no"):
                    data[field] = True if data[field].lower() == "yes" else False
                else:
                    invalid_fields.append(field)
        return (data, invalid_fields)

    @ResearchTaskAPI.exposed
    def add_lsb(self, response_id: str | UUID, data: dict[str, Any]) -> None:
        """Add LSB data to the response with id *response_id*."""
        response_id = self._cast_uuid(response_id)
        self.logger.info(
            f"Adding ratings for {self.__class__.__name__} response with id {response_id}.."
        )
        if response_id not in self._response_data:
            exc = ValueError(
                f"Failed to add ratings to {self.__class__.__name__} response with id "
                f"{response_id}: no response with this id in progress."
            )
            self.logger.error(str(exc))
            raise exc
        self.logger.debug(f"... ratings data: {data}")
        print("DATA RECEIVED:")
        from pprint import pprint
        pprint(data)
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
                f"Failed to add ratings to {self.__class__.__name__} response: "
                "one or more boolean-string fields for the LSB response contain "
                f"values other than 'yes' or 'no': {invalid_bools!s}."
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
        if "hearing_impariment" in data and data["hearing_impairment"] == "yes":
            required_fields.append("hearing_aid")
        if "vision_impairment" in data and data["vision_impairment"] == "yes":
            required_fields.append("vision_aid")
        if "vision_aid" in data and data["vision_aid"] == "yes":
            required_fields.append("vision_fully_corrected")
        missing = self._find_missing_keys(data, required_fields)
        if missing:
            exc = KeyError(
                f"Failed to add ratings to {self.__class__.__name__} response: "
                f"missing key(s): {missing!s} for LSB response."
            )
            self.logger.error(str(exc))
            raise exc
        # Extract residencies
        residencies_d: dict[int, tuple[str, str, str]] = dict()
        for key, value in data.copy().items():
            if key.startswith("residenciesName-"):
                i = key.removeprefix("residenciesName-")
                try:
                    int(i)
                except ValueError:
                    exc = KeyError(
                        f"Failed to add ratings to {self.__class__.__name__} response: "
                        f"invalid, non-integer index '{i}' for residencies field on LSB response."
                    )
                    self.logger.error(str(exc))
                    raise exc
                required_fields = (f"residenciesFrom-{i}", f"residenciesTo-{i}")
                missing = self._find_missing_keys(data, required_fields)
                if missing:
                    exc = KeyError(
                        f"Failed to add ratings to {self.__class__.__name__} response: "
                        f"missing key(s): {missing!s} for LSB response."
                    )
                    self.logger.error(str(exc))
                    raise exc
                if (data[key].strip()
                        and data[f"residenciesFrom-{i}"].strip()
                        and data[f"residenciesTo-{i}"].strip()):
                    # Only add if it's not actually an empty row
                    residencies_d[int(i)] = (
                        data[key],
                        data[f"residenciesFrom-{i}"] + "-01",
                        data[f"residenciesTo-{i}"] + "-01"
                    )
                del data[key]
                del data[f"residenciesFrom-{i}"]
                del data[f"residenciesTo-{i}"]
        residencies = []
        for _, (_location, _start, _end) in sorted(residencies_d.items()):
            residencies.append(LsbqeTaskResidency(location=_location, start=_start, end=_end))
        # Remove dependent fields that ought to be left blank based on given answers
        print("Sex:", data["sex"])
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
        print("Stored LSB Data:")
        self._response_data[response_id]["lsb"] = lsb
        pprint(self._response_data)
        self.set_location(f"ldb.html?instance={response_id}")


# Required so importers know which class defines the API
eel_api = LsbqeTaskAPI
