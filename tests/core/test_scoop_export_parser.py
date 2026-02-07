from app.core.scoop_export_parser import (
    _format_updated_timestamp,
    extract_first_json_value,
    parse_scoop_export,
)
from app.core.scoop_types import ScoopApp


def test_extract_first_json_value_skips_invalid_prefix_and_parses_json() -> None:
    text = "LOG: start\n{invalid-json\n###\n" + '{"apps":[]}'

    value = extract_first_json_value(text)

    assert value == {"apps": []}


def test_extract_first_json_value_returns_none_when_no_json_exists() -> None:
    assert extract_first_json_value("only plain log lines") is None


def test_format_updated_timestamp_formats_iso_like_value() -> None:
    assert (
        _format_updated_timestamp("2099-12-31T23:59:58+09:00") == "2099-12-31 23:59:58"
    )


def test_format_updated_timestamp_keeps_short_values() -> None:
    assert _format_updated_timestamp("unknown") == "unknown"


def test_parse_scoop_export_parses_json_after_noisy_prefix() -> None:
    text = (
        "INFO: scoop export started\n"
        '{"apps":["skip-this",{"Name":"alpha-tool","Version":101,"Source":"bucket-a",'
        '"Updated":"2026-02-07T12:34:56+09:00","Info":"Demo package"}]}'
    )

    apps = parse_scoop_export(text)

    assert apps == [
        ScoopApp(
            name="alpha-tool",
            version="101",
            source="bucket-a",
            updated="2026-02-07 12:34:56",
            info="Demo package",
        )
    ]


def test_parse_scoop_export_returns_none_for_unexpected_structure() -> None:
    assert parse_scoop_export('{"items": []}') is None
    assert parse_scoop_export('{"apps": "not-a-list"}') is None
