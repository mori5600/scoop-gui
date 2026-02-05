import re

from .scoop_export_parser import extract_first_json_value
from .scoop_types import ScoopSearchResult

# Scoop prints via PowerShell formatting, which can include ANSI sequences.
_ANSI_OSC_RE = re.compile(r"\x1b\][^\x07]*(?:\x07|\x1b\\)")
_ANSI_CSI_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
_ANSI_2CHAR_RE = re.compile(r"\x1b[@-Z\\-_]")


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
            name = str(item.get("Name") or item.get("name") or "").strip()
            if not name:
                continue

            version = str(item.get("Version") or item.get("version") or "").strip()
            source = str(item.get("Source") or item.get("source") or "").strip()
            binaries = str(item.get("Binaries") or item.get("binaries") or "").strip()

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
