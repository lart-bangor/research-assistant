"""API to exposes the LSBQe to Python Eel."""

import logging
from typing import Any

from ...booteel.task_api import ResearchTaskAPI
from ...booteel import errors
from ...config import config
from ...datamodels.types import AnyUUID
from .datamodel import (
    LdbLanguageInformation,
    LdbParentInformation,
    LdbResponse,
    LsbResponse,
    LsbResidency,
    LsbqeResponse,
    ClubResponse,
    ClubActivities,
    ClubCodeSwitching,
    ClubLifeStages,
    ClubPeopleChildhood,
    ClubPeopleCurrent,
    ClubSituations,
)

logger = logging.getLogger(__name__)


class LsbqeTaskAPI(ResearchTaskAPI):
    """Eel API for the LSBQe Task."""

    logger = logger
    response_class = LsbqeResponse
    task_version = "0.5.0a0"
    task_data_path = config.paths.data / "LSBQe"
    eel_namespace = "lsbqe"

    @ResearchTaskAPI.exposed
    def add_lsb(self, response_id: AnyUUID, data: dict[str, Any]) -> None:  # noqa: C901
        """Add LSB data to the response with id *response_id*."""
        response_id = self._cast_uuid(response_id)
        self._response_exists_or_fail(response_id)
        self.logger.info(
            f"Adding {self._task_name}.lsb data to response with id {response_id}.."
        )
        self.logger.debug(f"... data={data}")
        # Make booleans
        fields_to_cast = (
            "vision_impairment",
            "vision_aid",
            "vision_fully_corrected",
            "hearing_impairment",
            "hearing_aid",
        )
        data, invalid_bools = self._cast_bools(data, fields_to_cast)
        if invalid_bools:
            raise errors.InvalidValueError(
                (
                    f"One or more boolean fields for {self._task_name}.lsb data contain "
                    f"values other than ('yes', 'no', 'true', 'false', 0, 1): {invalid_bools!r}"
                ),
                task=self._task_name,
                response_id=response_id,
            )
        # Check for missing required fields
        required_fields = [
            "sex",
            "occupation",
            "handedness",
            "date_of_birth",
            "hearing_impairment",
            "vision_impairment",
            "place_of_birth",
            "education_level",
        ]
        if "sex" in data and data["sex"] == "o":
            required_fields.append("sex_other")
        if "hearing_impariment" in data and data["hearing_impairment"]:
            required_fields.append("hearing_aid")
        if "vision_impairment" in data and data["vision_impairment"]:
            required_fields.append("vision_aid")
        if "vision_aid" in data and data["vision_aid"]:
            required_fields.append("vision_fully_corrected")
        if missing := self._find_missing_keys(data, required_fields):
            raise errors.MissingKeysError(
                (
                    f"Failed to add {self._task_name}.lsb data: "
                    f"missing key(s) {missing!r}"
                ),
                task=self._task_name,
                missing_keys=missing,
                response_id=response_id,
            )
        # Extract residencies
        residencies_d: dict[int, tuple[str, str, str]] = dict()
        for key in data.keys():
            if key.startswith("residencies-") and key.endswith("-name"):
                try:
                    i = key.split("-")[1]
                    int(i)
                except IndexError:
                    raise errors.InvalidKeyError(
                        (
                            f"Failed to add {self._task_name}.lsb data: invalid, non-indexed "
                            f"key '{key}' for 'residencies-' field"
                        ),
                        task=self._task_name,
                        response_id=response_id,
                    )
                except ValueError:
                    raise errors.InvalidKeyError(
                        (
                            f"Failed to add {self._task_name}.lsb data: invalid, non-integer "
                            f"index '{i}' for 'residencies-' field"
                        ),
                        task=self._task_name,
                        response_id=response_id,
                    )
                required_fields = (
                    f"residencies-{i}-from",
                    f"residencies-{i}-to",
                )
                if missing := self._find_missing_keys(data, required_fields):
                    raise errors.MissingKeysError(
                        (
                            f"Failed to add {self._task_name}.lsb.residencies data: "
                            f"missing key(s) {missing!s}"
                        ),
                        task=self._task_name,
                        response_id=response_id,
                    )
                if (
                    data[key].strip()
                    or data[f"residencies-{i}-from"].strip()
                    or data[f"residencies-{i}-to"].strip()
                ):
                    # Only add if it's not actually an empty row, but be happy
                    # enough here with at least one of them being non-empty so
                    # that we hit validation errors later if applicable.
                    residencies_d[int(i)] = (
                        data[key],
                        data[f"residencies-{i}-from"] + "-01",
                        data[f"residencies-{i}-to"] + "-01",
                    )
        residencies = []
        for _, (_location, _start, _end) in sorted(residencies_d.items()):
            residencies.append(
                LsbResidency(location=_location, start=_start, end=_end)
            )
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
        if (
            "vision_fully_corrected" in data
            and "vision_aid" in data
            and not data["vision_aid"]
        ):
            del data["vision_fully_corrected"]
        self.logger.debug(f"... cleaned data={data!r}")
        # Construct the LSB response object
        lsb = LsbResponse(
            sex=data["sex"],
            sex_other=(data["sex_other"] if data["sex_other"] else None),
            occupation=data["occupation"],
            handedness=data["handedness"],
            date_of_birth=data["date_of_birth"],
            hearing_impairment=data["hearing_impairment"],
            hearing_aid=(data["hearing_aid"] if "hearing_aid" in data else None),
            vision_impairment=data["vision_impairment"],
            vision_aid=(data["vision_aid"] if "vision_aid" in data else None),
            vision_fully_corrected=(
                data["vision_fully_corrected"]
                if "vision_fully_corrected" in data
                else None
            ),
            place_of_birth=data["place_of_birth"],
            residencies=residencies,
            education_level=data["education_level"],
        )
        self._response_data[response_id]["lsb"] = lsb
        self.set_location(f"ldb.html?instance={response_id}")

    @ResearchTaskAPI.exposed
    def add_ldb(self, response_id: AnyUUID, data: dict[str, Any]) -> None:  # noqa: C901
        """Add LDB data to the response with id *response_id*."""
        response_id = self._cast_uuid(response_id)
        self._response_exists_or_fail(response_id)
        self.logger.info(
            f"Adding {self._task_name}.ldb response with id {response_id}.."
        )
        self.logger.debug(f"... data={data!r}")
        # Make booleans
        fields_to_cast = (
            "father_not_applicable",
            "mother_not_applicable",
        )
        data, invalid_bools = self._cast_bools(data, fields_to_cast)
        if invalid_bools:
            raise errors.InvalidValueError(
                (
                    f"One or more boolean fields for {self._task_name}.ldb data contain "
                    f"values other than ('yes', 'no', 'true', 'false', 0, 1): {invalid_bools!r}"
                ),
                task=self._task_name,
                response_id=response_id,
            )
        # Supply defaults for father/mother_not_applicable
        if "father_not_applicable" not in data:
            data["father_not_applicable"] = False
        if "mother_not_applicable" not in data:
            data["mother_not_applicable"] = False
        # Check for missing required fields
        required_fields = []
        if not data["father_not_applicable"]:
            required_fields.extend(
                (
                    "father_education_level",
                    "father_occupation",
                    "father_first_language",
                    "father_second_language",
                    "father_other_languages",
                )
            )
        if not data["mother_not_applicable"]:
            required_fields.extend(
                (
                    "mother_education_level",
                    "mother_occupation",
                    "mother_first_language",
                    "mother_second_language",
                    "mother_other_languages",
                )
            )
        if missing := self._find_missing_keys(data, required_fields):
            raise errors.MissingKeysError(
                (
                    f"Failed to add {self._task_name}.ldb data: "
                    f"missing key(s) {missing!r}"
                ),
                task=self._task_name,
                missing_keys=missing,
                response_id=response_id,
            )
        # Prepare parental information
        parent_info: list[LdbParentInformation] = []
        if not data["father_not_applicable"]:
            father = LdbParentInformation(
                parent="father",
                occupation=data["father_occupation"],
                first_language=data["father_first_language"],
                second_language=data["father_second_language"].strip() or None,
                other_languages=data["father_other_languages"].strip() or None,
            )
            parent_info.append(father)
        if not data["mother_not_applicable"]:
            mother = LdbParentInformation(
                parent="mother",
                occupation=data["mother_occupation"],
                first_language=data["mother_first_language"],
                second_language=data["mother_second_language"].strip() or None,
                other_languages=data["mother_other_languages"].strip() or None,
            )
            parent_info.append(mother)
        # Extract languages_spoken-X data
        languages_spoken: list[LdbLanguageInformation] = []
        for key in data.keys():
            if key.startswith("languages_spoken-") and key.endswith("-name"):
                try:
                    i = key.split("-")[1]
                    int(i)
                except IndexError:
                    raise errors.InvalidKeyError(
                        (
                            f"Failed to add {self._task_name}.ldb data: invalid, non-indexed "
                            f"key '{key}' for 'languages_spoken-' field"
                        ),
                        task=self._task_name,
                        response_id=response_id,
                    )
                except ValueError:
                    raise errors.InvalidKeyError(
                        (
                            f"Failed to add {self._task_name}.ldb data: invalid, non-integer "
                            f"index '{i}' for 'languages_spoken-' field"
                        ),
                        task=self._task_name,
                        response_id=response_id,
                    )
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
                if f"languages_spoken-{i}-source" in data:
                    try:
                        data[f"languages_spoken-{i}-source"] = [
                            s.lower() for s in data[f"languages_spoken-{i}-source"]
                        ]
                    except Exception:
                        pass
                    if "o" in data[f"languages_spoken-{i}-source"]:
                        required_fields.append(f"languages_spoken-{i}-source_other")
                if missing := self._find_missing_keys(data, required_fields):
                    raise errors.MissingKeysError(
                        (
                            f"Failed to add {self._task_name}.ldb.languages_spoken data: "
                            f"missing key(s) {missing!r}"
                        ),
                        task=self._task_name,
                        missing_keys=missing,
                        response_id=response_id,
                    )
                source_other = None
                if "o" in data[f"languages_spoken-{i}-source"]:
                    source_other = data[f"languages_spoken-{i}-source_other"].strip()
                    if not source_other:
                        raise errors.InvalidValueError(
                            (
                                f"Failed to add {self._task_name}.ldb.languages_spoken data: "
                                f"required field `languages_spoken-{i}-source_other` is empty"
                            ),
                            task=self._task_name,
                            response_id=response_id,
                        )
                breaks = 0
                fields_to_cast = (
                    f"languages_spoken-{i}-break_years",
                    f"languages_spoken-{i}-break_months",
                )
                data, invalid_ints = self._cast_ints(data, fields_to_cast)
                if invalid_ints:
                    raise errors.InvalidValueError(
                        (
                            f"One or more integer fields for {self._task_name}.ldb.languages_spoken"
                            f" data contain values that cannot be cast to int: {invalid_ints!r}"
                        ),
                        task=self._task_name,
                        response_id=response_id,
                    )
                breaks += data[f"languages_spoken-{i}-break_years"] * 12
                breaks += data[f"languages_spoken-{i}-break_months"]
                fields_to_cast = (
                    f"languages_spoken-{i}-proficiency_speaking",
                    f"languages_spoken-{i}-proficiency_understanding",
                    f"languages_spoken-{i}-proficiency_reading",
                    f"languages_spoken-{i}-proficiency_writing",
                    f"languages_spoken-{i}-usage_speaking",
                    f"languages_spoken-{i}-usage_listening",
                    f"languages_spoken-{i}-usage_reading",
                    f"languages_spoken-{i}-usage_writing",
                )
                data, invalid_floats = self._cast_floats(data, fields_to_cast)
                if invalid_floats:
                    raise errors.InvalidValueError(
                        (
                            f"One or more float fields for {self._task_name}.ldb.languages_spoken"
                            " data contain values that cannot be cast to float:"
                            f" {invalid_floats!r}"
                        ),
                        task=self._task_name,
                        response_id=response_id,
                    )
                prof_speak = data[f"languages_spoken-{i}-proficiency_speaking"]
                prof_under = data[f"languages_spoken-{i}-proficiency_understanding"]
                prof_read = None
                prof_write = None
                usage_speak = data[f"languages_spoken-{i}-usage_speaking"]
                usage_listn = data[f"languages_spoken-{i}-usage_listening"]
                usage_read = None
                usage_write = None
                if f"languages_spoken-{i}-proficiency_reading" in data:
                    prof_read = data[f"languages_spoken-{i}-proficiency_reading"]
                if f"languages_spoken-{i}-proficiency_writing" in data:
                    prof_write = data[f"languages_spoken-{i}-proficiency_writing"]
                if f"languages_spoken-{i}-usage_reading" in data:
                    usage_read = data[f"languages_spoken-{i}-usage_reading"]
                if f"languages_spoken-{i}-usage_writing" in data:
                    usage_write = data[f"languages_spoken-{i}-usage_writing"]
                language_spoken = LdbLanguageInformation(
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
                    usage_writing=usage_write,
                )
                languages_spoken.append(language_spoken)
        ldb = LdbResponse(languages=languages_spoken, parents=parent_info)
        self._response_data[response_id]["ldb"] = ldb
        self.set_location(f"club.html?instance={response_id}")

    @ResearchTaskAPI.exposed
    def add_club(  # noqa: C901
        self, response_id: AnyUUID, data: dict[str, Any]
    ) -> None:
        """Add CLUB data to the response with id *response_id*."""
        response_id = self._cast_uuid(response_id)
        self._response_exists_or_fail(response_id)
        self.logger.info(
            f"Adding {self._task_name}.club data to response with id {response_id}.."
        )
        self.logger.debug(f"... data={data}")
        # Check for missing fields
        always_required = (
            "life_stage-infancy_age",
            "life_stage-nursery_age",
            "life_stage-primary_age",
            "life_stage-secondary_age",
        )
        maybe_na = [
            "people_current-parents",
            "people_current-children",
            "people_current-siblings",
            "people_current-grandparents",
            "people_current-other_relatives",
            "people_current-partner",
            "people_current-friends",
            "people_current-flatmates",
            "people_current-neighbours",
            "people_childhood-parents",
            "people_childhood-siblings",
            "people_childhood-grandparents",
            "people_childhood-other_relatives",
            "people_childhood-friends",
            "people_childhood-neighbours",
            "situation-home",
            "situation-school",
            "situation-work",
            "situation-socialising",
            "situation-religion",
            "situation-leisure",
            "situation-commercial",
            "situation-public",
            "activity-reading",
            "activity-emailing",
            "activity-texting",
            "activity-social_media",
            "activity-notes",
            "activity-traditional_media",
            "activity-internet",
            "activity-praying",
        ]
        cs_fields = (
            "code_switching-parents_and_family",
            "code_switching-friends",
            "code_switching-social_media",
        )
        for cs_field in cs_fields:
            if cs_field in data or f"{cs_field}-not_applicable" in data:
                # If any one is present, all are "maybe_na's"
                maybe_na.extend(cs_fields)
                break
        # Cast booleans for -not_applicable options
        fields_to_cast = (f"{field}-not_applicable" for field in maybe_na)
        data, invalid_bools = self._cast_bools(data, fields_to_cast)
        if invalid_bools:
            raise errors.InvalidValueError(
                (
                    f"One or more boolean fields for {self._task_name}.club data contain "
                    f"values other than ('yes', 'no', 'true', 'false', 0, 1): {invalid_bools!r}"
                ),
                task=self._task_name,
                response_id=response_id,
            )
        # Set all maybe_na fields that are marked as N/A to None
        for candidate in maybe_na:
            na_option = f"{candidate}-not_applicable"
            if na_option in data and data[na_option]:
                data[candidate] = None
        required_fields = maybe_na[:]
        required_fields.extend(always_required)
        if missing := self._find_missing_keys(data, required_fields):
            raise errors.MissingKeysError(
                (
                    f"Failed to add {self._task_name}.club data: "
                    f"missing key(s) {missing!r}"
                ),
                task=self._task_name,
                missing_keys=missing,
                response_id=response_id,
            )
        # Cast floats
        fields_to_cast = [field for field in maybe_na if data[field] is not None]
        fields_to_cast.append(always_required)
        data, invalid_floats = self._cast_floats(data, fields_to_cast)
        if invalid_floats:
            raise errors.InvalidValueError(
                (
                    f"One or more float fields for {self._task_name}.club"
                    f" data contain values that cannot be cast to float: {invalid_floats!r}"
                ),
                task=self._task_name,
                response_id=response_id,
            )
        # Build CLUB components
        life_stages = ClubLifeStages(
            infancy_age=data["life_stage-infancy_age"],
            nursery_age=data["life_stage-nursery_age"],
            primary_age=data["life_stage-primary_age"],
            secondary_age=data["life_stage-secondary_age"],
        )
        people_current = ClubPeopleCurrent(
            parents=data["people_current-parents"],
            children=data["people_current-children"],
            siblings=data["people_current-siblings"],
            grandparents=data["people_current-grandparents"],
            other_relatives=data["people_current-other_relatives"],
            partner=data["people_current-partner"],
            friends=data["people_current-friends"],
            flatmates=data["people_current-flatmates"],
            neighbours=data["people_current-neighbours"],
        )
        people_childhood = ClubPeopleChildhood(
            parents=data["people_childhood-parents"],
            siblings=data["people_childhood-siblings"],
            grandparents=data["people_childhood-grandparents"],
            other_relatives=data["people_childhood-other_relatives"],
            friends=data["people_childhood-friends"],
            neighbours=data["people_childhood-neighbours"],
        )
        situations = ClubSituations(
            home=data["situation-home"],
            school=data["situation-school"],
            work=data["situation-work"],
            socialising=data["situation-socialising"],
            religion=data["situation-religion"],
            leisure=data["situation-leisure"],
            commercial=data["situation-commercial"],
            public=data["situation-public"],
        )
        activities = ClubActivities(
            reading=data["activity-reading"],
            emailing=data["activity-emailing"],
            texting=data["activity-texting"],
            social_media=data["activity-social_media"],
            notes=data["activity-notes"],
            traditional_media=data["activity-traditional_media"],
            internet=data["activity-internet"],
            praying=data["activity-praying"],
        )
        code_switching = None
        if cs_fields[0] in data:
            code_switching = ClubCodeSwitching(
                parents_and_family=data["code_switching-parents_and_family"],
                friends=data["code_switching-friends"],
                social_media=data["code_switching-social_media"],
            )
        club = ClubResponse(
            life_stages=life_stages,
            people_current=people_current,
            people_childhood=people_childhood,
            situations=situations,
            activities=activities,
            code_switching=code_switching,
        )
        self._response_data[response_id]["club"] = club
        self.set_location(f"end.html?instance={response_id}")

    @ResearchTaskAPI.exposed
    def add_note(self, response_id: AnyUUID, data: dict[str, Any]):
        """Add participant note to the response with id *response_id*.

        Note that this method does not redirect or confirm the addition of the note.
        If unsuccessful either a `errors.MissingKeysError` or `errors.InvalidValueError`
        will be raised. To add a participant note and store the complete response
        in one go use the `add_note_and_end()` method instead.
        """
        response_id = self._cast_uuid(response_id)
        self._response_exists_or_fail(response_id)
        self.logger.info(
            f"Adding {self._task_name}.note data to response with id {response_id}.."
        )
        self.logger.debug(f"... data={data}")
        if missing := self._find_missing_keys(
            data,
            [
                "participant_note",
            ],
        ):
            raise errors.MissingKeysError(
                (
                    f"Failed to add {self._task_name}.note data: "
                    f"missing key(s) {missing!r}"
                ),
                task=self._task_name,
                missing_keys=missing,
                response_id=response_id,
            )
        if isinstance(data["participant_note"], (bytes, bytearray)):
            data["participant_note"] = data["participant_note"].decode("utf-8")
        if not isinstance(data["participant_note"], str):
            raise errors.InvalidValueError(
                (
                    f"One or more string fields for {self._task_name}.note data contain "
                    f"non-string data: type(participant_note)={type(data['participant_note'])!r}"
                ),
                task=self._task_name,
                response_id=response_id,
            )
        data["participant_note"] = data["participant_note"].strip()
        if data["participant_note"]:
            self._response_data[response_id]["note"] = data["participant_note"]
        else:
            self._response_data[response_id]["note"] = None

    @ResearchTaskAPI.exposed
    def add_note_and_end(self, response_id: AnyUUID, data: dict[str, Any]) -> str:
        """Optionally add a participant note, store response, and direct to next task."""
        self.add_note(response_id, data)
        self.store(response_id)
        self.end(response_id)


# Required so importers know which class defines the API
eel_api = LsbqeTaskAPI
