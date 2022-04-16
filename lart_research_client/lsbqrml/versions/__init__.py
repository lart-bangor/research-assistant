"""Version implementations and translations for the LSBQ-RML."""
from typing import Any
from importlib import resources
import json
from lsbqrml import logger


def _get_versions() -> dict[str, dict[str, Any]]:
    """Loads all available LSBQ-RML versions into memory."""
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
