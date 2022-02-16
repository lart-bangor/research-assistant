"""Data structures for the Language and Social Background Questionnaire for Regional and Minority Languages
"""
from typing import Any, Optional
from datavalidator import DataValidator

class LsbqRml:

    data: dict[str, Any] = {}

    def __init__(self, version: str, researcher_id: str, research_location: str, participant_id: str, consent: bool, date: Optional[str] = None):
        # Validate each initialisation field
        vr = DataValidator(forcecast=True)
        self.data["version"] = vr.validatestring("LSBQ-RML version identifier", r"\w{13, 17}", version).data
        self.data["researcher_id"] = vr.validatestring("Researcher ID", r"[A-Za-z0-9]{3,10}", researcher_id).data
        self.data["research_location"] = vr.validatestring("location name", r"[A-Za-z0-9, \(\)]{1,50}", research_location).data
        self.data["participant_id"] = vr.validatestring("Participant ID", r"[A-Za-z0-9]{3,10}", participant_id).data
        self.data["consent"] = vr.validatebool("consent confirmation", ({"on", "yes", "true", 1, "1"}, {"off", "no", "false", 0, "0"}), consent, softcast=True, forcecast=False).data
        # TODO: Add logic to insert and handle date (need to settle on format - maybe check what bootstrap form returns?)
        vr.raiseif()
