from dataclasses import FrozenInstanceError

import pytest

from app.core.scoop_types import ScoopApp, ScoopSearchResult


def test_scoop_app_default_fields_are_empty_strings() -> None:
    item = ScoopApp(name="alpha-tool", version="1.0.0")

    assert item.name == "alpha-tool"
    assert item.version == "1.0.0"
    assert item.source == ""
    assert item.updated == ""
    assert item.info == ""


def test_scoop_search_result_default_fields_are_empty_strings() -> None:
    result = ScoopSearchResult(name="beta-item")

    assert result.name == "beta-item"
    assert result.version == ""
    assert result.source == ""
    assert result.binaries == ""


def test_scoop_types_are_frozen_dataclasses() -> None:
    result = ScoopSearchResult(name="gamma-item")

    with pytest.raises(FrozenInstanceError):
        result.name = "changed"  # type: ignore[misc]
