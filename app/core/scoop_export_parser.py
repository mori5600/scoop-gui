import json
from typing import Any

from .scoop_types import ScoopApp


def extract_first_json_value(text: str) -> Any | None:
    """Extracts the first JSON value from a noisy text stream.

    This is tolerant to non-JSON prefixes (e.g. banner/log lines). It attempts to decode
    JSON starting at each '{' or '[' occurrence.

    Args:
        text: Text that may contain a JSON value.

    Returns:
        The parsed JSON value, or None if no valid JSON value is found.
    """
    decoder = json.JSONDecoder()
    for i, ch in enumerate(text):
        if ch not in "{[":
            continue
        try:
            value, _ = decoder.raw_decode(text, i)
            return value
        except json.JSONDecodeError:
            continue
    return None


def _format_updated_timestamp(value: str) -> str:
    """Formats Scoop timestamp strings for display.

    Args:
        value: Timestamp string (usually ISO 8601) from Scoop output.

    Returns:
        A display-friendly timestamp string.
    """
    if len(value) >= 19:
        return value[:19].replace("T", " ")
    return value


def parse_scoop_export(text: str) -> list[ScoopApp] | None:
    """Parses `scoop export` JSON output into a list of apps.

    Args:
        text: `scoop export` stdout text (may contain extra non-JSON lines).

    Returns:
        A list of installed apps, or None if the JSON cannot be parsed or has an unexpected
        structure.
    """
    data = extract_first_json_value(text)
    if not (isinstance(data, dict) and isinstance(data.get("apps"), list)):
        return None

    apps: list[ScoopApp] = []
    for item in data["apps"]:
        if not isinstance(item, dict):
            continue
        apps.append(
            ScoopApp(
                name=str(item.get("Name", "")),
                version=str(item.get("Version", "")),
                source=str(item.get("Source", "")),
                updated=_format_updated_timestamp(str(item.get("Updated", ""))),
                info=str(item.get("Info", "")),
            )
        )
    return apps
