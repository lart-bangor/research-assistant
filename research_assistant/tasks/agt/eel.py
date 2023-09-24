"""API to expose the AGT Task to Python Eel."""
import logging
from uuid import UUID
from random import sample, shuffle
from typing import Final, Any
from ...task_api import ResearchTaskAPI
from ...config import config
from .datamodel import AgtTaskTraitRating, AgtTaskTrialRatings, AgtTaskResponse

logger = logging.getLogger(__name__)


class AgtTaskAPI(ResearchTaskAPI):
    """Eel API for the AGT Task."""

    logger = logger
    response_class = AgtTaskResponse
    task_version = "0.5.0a0"
    task_data_path = config.paths.data / "AGT"
    eel_namespace = "agt"

    # agt_practice_trials: Final[tuple[str, ...]] = (
    #     "practice",     # Practice trial
    # )

    # agt_filler_trials: Final[tuple[str, ...]] = (
    #     "f1",           # Filler 1
    #     "f2",           # Filler 2
    #     "f3",           # Filler 3
    #     "f4",           # Filler 4
    # )

    # agt_guise_trials: Final[tuple[str, ...]] = (
    #     "s1_maj",    # 1st recording of variety 1
    #     "s1_rml",    # 1st recording of variety 2
    #     "s2_maj",    # 2nd recording of variety 1
    #     "s2_rml",    # 2md recording of variety 2
    #     "s3_maj",    # 3rd recording of variety 1
    #     "s3_rml",    # 3rd recording of variety 2
    #     "s4_maj",    # 4th recording of variety 1
    #     "s4_rml",    # 4th recording of variety 2
    # )

    # agt_trials: Final[tuple[str, ...]] = agt_practice_trials + agt_filler_trials + agt_guise_trials

    agt_traits: Final[tuple[str, ...]] = (
        "amusing",
        "open-minded",
        "attractive",
        "trustworthy",
        "ignorant",
        "polite",
        "ambitious",
        "international",
        "cool",
        "intelligent",
        "influential",
        "likeable",
        "educated",
        "friendly",
        "honest",
        "competent",
        "natural",
        "pretentious",
    )

    @ResearchTaskAPI.exposed
    def get_traits(self) -> list[str]:
        """Return a randomised list of AGT traits for rating."""
        return sample(self.agt_traits, k=len(self.agt_traits))

    @ResearchTaskAPI.exposed
    def get_trials(self) -> list[str]:
        """Return a randomised list of AGT stimuli for the trials.

        This produces a pseudo-randomised AGT presentation order.

        Given four speakers, four fillers, and two languages,
        produce a presentation order for Matched Guise Task,
        based on the following grid:

        +---------+----------+-----------------------+
        | Speaker | Language | Example               |
        +=========+==========+=======================+
        | F1      | Either   | Filler 1              |
        +---------+----------+-----------------------+
        | S1      | L1       | Speaker 1, Language 1 |
        +---------+----------+-----------------------+
        | S2      | L2       | Speaker 2, Language 2 |
        +---------+----------+-----------------------+
        | F2      | Either   | Filler 2              |
        +---------+----------+-----------------------+
        | S3      | L2       | Speaker 3, Language 2 |
        +---------+----------+-----------------------+
        | S4      | L1       | Speaker 4, Language 1 |
        +---------+----------+-----------------------+
        | F3      | Either   | Filler 3              |
        +---------+----------+-----------------------+
        | S1      | L2       | Speaker 1, Language 2 |
        +---------+----------+-----------------------+
        | S2      | L1       | Speaker 2, Language 1 |
        +---------+----------+-----------------------+
        | F4      | Either   | Filler 4              |
        +---------+----------+-----------------------+
        | S3      | L1       | Speaker 3, Language 1 |
        +---------+----------+-----------------------+
        | S4      | L2       | Speaker 4, Language 2 |
        +---------+----------+-----------------------+

        The function randomises:
            (a) the order of the fillers (regardless of filler language),
            (b) the order in which speakers are presented (distance kept constant)
            (c) whether L1 or L2 are presented first (keeping alternation constant)
        """
        # Parameters
        fillers = ["f1", "f2", "f3", "f4"]
        speakers = ["s1", "s2", "s3", "s4"]
        languages = ["maj", "rml"]
        sep = "_"

        # Validate parameters
        if (len(fillers), len(speakers), len(languages)) != (4, 4, 2):
            raise ValueError(
                "Wrong list length for parameters: 4 fillers, 4 speakers and "
                "2 languages required."
            )

        # Randomise parameters
        shuffle(fillers)
        shuffle(speakers)
        shuffle(languages)

        # Build order
        order: tuple[str, ...] = (
            fillers[0],
            f"{speakers[0]}{sep}{languages[0]}",
            f"{speakers[1]}{sep}{languages[1]}",
            fillers[1],
            f"{speakers[2]}{sep}{languages[1]}",
            f"{speakers[3]}{sep}{languages[0]}",
            fillers[2],
            f"{speakers[0]}{sep}{languages[1]}",
            f"{speakers[1]}{sep}{languages[0]}",
            fillers[3],
            f"{speakers[2]}{sep}{languages[0]}",
            f"{speakers[3]}{sep}{languages[1]}",
        )

        return order

    @ResearchTaskAPI.exposed
    def add_ratings(self, response_id: str | UUID, data: dict[str, Any]):
        """Add AGT ratings for one trial to the response with id *response_id*."""
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
        if "trial" not in data:
            exc = KeyError(
                f"Failed to add ratings to {self.__class__.__name__} response: "
                "missing 'trial' value."
            )
            self.logger.error(str(exc))
            raise exc
        trial = str(data["trial"])
        trait_keys = {f"trait-{trait}": trait for trait in self.agt_traits}
        missing = self._find_missing_keys(data, trait_keys.keys())
        if missing:
            exc = KeyError(
                f"Failed to add ratings to {self.__class__.__name__} response: "
                f"missing trait rating keys {missing!r}."
            )
            self.logger.error(str(exc))
            raise exc
        trait_ratings: list[AgtTaskTraitRating] = []
        for key, trait in trait_keys.items():
            trait_ratings.append(AgtTaskTraitRating(trait=trait, rating=float(data[key])))
        trial_ratings = AgtTaskTrialRatings(trial=trial, ratings=trait_ratings)
        print(trial_ratings)




# Required so importers know which class defines the API
eel_api = AgtTaskAPI
