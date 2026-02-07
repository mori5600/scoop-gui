import re

from .scoop_export_parser import extract_first_json_value
from .scoop_types import ScoopSearchResult

# Scoop prints via PowerShell formatting, which can include ANSI sequences.
_ANSI_OSC_RE = re.compile(r"\x1b\][^\x07]*(?:\x07|\x1b\\)")
_ANSI_CSI_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
_ANSI_2CHAR_RE = re.compile(r"\x1b[@-Z\\-_]")


def _coerce_text(value: object) -> str:
    """Converts parsed JSON field values into plain display text."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (int, float, bool)):
        return str(value).strip()
    if isinstance(value, list):
        parts = []
        for v in value:
            text = _coerce_text(v)
            if text:
                parts.append(text)
        return " ".join(parts).strip()
    if isinstance(value, dict):
        # PowerShell can serialize JsonElement-like values into only `ValueKind`.
        if set(value.keys()) <= {"ValueKind"}:
            return ""
        return ""
    return str(value).strip()


def _sanitize(text: str) -> str:
    """Normalizes newlines and strips common ANSI escape sequences."""
    if not text:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = _ANSI_OSC_RE.sub("", text)
    text = _ANSI_CSI_RE.sub("", text)
    text = _ANSI_2CHAR_RE.sub("", text)
    return text


def parse_scoop_search(text: str) -> list[ScoopSearchResult]:
    """Parses `scoop search` output into rows.

    Preferred input is JSON emitted by an explicit `ConvertTo-Json` pipeline (more
    stable across PowerShell versions). A formatted-table fallback is kept for
    resilience.
    """
    results: list[ScoopSearchResult] = []

    data = extract_first_json_value(text)
    if isinstance(data, dict):
        data = [data]

    if isinstance(data, list):
        for item in data:
            if not isinstance(item, dict):
                continue

            # Keys are capitalized by our PowerShell pipeline, but keep a small
            # fallback set for safety.
            name = _coerce_text(item.get("Name") or item.get("name") or "")
            if not name:
                continue

            version = _coerce_text(item.get("Version") or item.get("version") or "")
            source = _coerce_text(item.get("Source") or item.get("source") or "")
            binaries = _coerce_text(item.get("Binaries") or item.get("binaries") or "")

            results.append(
                ScoopSearchResult(
                    name=name,
                    version=version,
                    source=source,
                    binaries=binaries,
                )
            )
        return results

    # ---- Fallback: parse formatted text table
    text = _sanitize(text)

    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue

        lower = s.lower()
        if lower.startswith("results from"):
            continue
        if lower.startswith("name") and "version" in lower and "source" in lower:
            continue
        if s and all(ch == "-" for ch in s.replace(" ", "")):
            continue

        parts = re.split(r"\s{2,}", s)
        if len(parts) < 1:
            continue

        # Expected: Name, Version, Source, Binaries (last is optional).
        name = parts[0].strip()
        if not name:
            continue

        version = parts[1].strip() if len(parts) >= 2 else ""
        source = parts[2].strip() if len(parts) >= 3 else ""
        binaries = (
            "  ".join(p.strip() for p in parts[3:] if p.strip())
            if len(parts) >= 4
            else ""
        )

        results.append(
            ScoopSearchResult(
                name=name,
                version=version,
                source=source,
                binaries=binaries,
            )
        )

    return results
