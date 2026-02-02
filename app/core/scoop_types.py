from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ScoopApp:
    """Represents an installed Scoop app.

    Attributes:
        name: App name.
        version: Installed version string.
        source: Bucket name (e.g. "main").
        updated: Timestamp string (best-effort).
        info: Additional info (best-effort).
    """

    name: str
    version: str
    source: str = ""
    updated: str = ""
    info: str = ""
