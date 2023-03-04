"""Version implementations and translations for the LSBQe."""
import logging
import json
from importlib import resources
from typing import Any

logger = logging.getLogger(__name__)


def _get_versions() -> dict[str, dict[str, Any]]:
    """Loads all available LSBQe versions into memory."""
    versions: dict[str, dict[str, Any]] = {}
    for item in resources.contents(__name__):
        if resources.is_resource(__name__, item) and item[-5:] == ".json":
            with resources.open_text(__name__, item) as fp:
                buf = json.load(fp)
                if "meta" in buf and "versionId" in buf["meta"]:
                    versions[buf["meta"]["versionId"]] = buf
                else:
                    logger.error(
                        f"Resource '{__name__}/{item}' is missing key 'meta.versionId'."
                    )
    return versions


versions = _get_versions()
