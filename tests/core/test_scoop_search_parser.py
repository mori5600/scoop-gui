from app.core.scoop_search_parser import _sanitize, parse_scoop_search
from app.core.scoop_types import ScoopSearchResult


def test_parse_scoop_search_reads_json_and_skips_rows_without_name() -> None:
    text = (
        "INFO: searching...\n"
        '[{"Name":"alpha-tool","Version":"1.2.3","Source":"bucket-a","Binaries":"alpha.exe"},'
        '{"name":"beta-archive","version":"4.5.6","source":"bucket-b","binaries":"beta.exe"},'
        '{"Version":"1.0.0"}]'
    )

    results = parse_scoop_search(text)

    assert results == [
        ScoopSearchResult(
            name="alpha-tool",
            version="1.2.3",
            source="bucket-a",
            binaries="alpha.exe",
        ),
        ScoopSearchResult(
            name="beta-archive",
            version="4.5.6",
            source="bucket-b",
            binaries="beta.exe",
        ),
    ]


def test_parse_scoop_search_accepts_single_json_object() -> None:
    text = (
        '{"Name":"gamma-suite","Version":"9.9.9","Source":"bucket-c",'
        '"Binaries":"gamma.exe"}'
    )

    results = parse_scoop_search(text)

    assert results == [
        ScoopSearchResult(
            name="gamma-suite",
            version="9.9.9",
            source="bucket-c",
            binaries="gamma.exe",
        )
    ]


def test_parse_scoop_search_ignores_valuekind_objects() -> None:
    text = (
        '[{"Name":"sample-tool","Version":{"ValueKind":3},"Source":"sample-bucket",'
        '"Binaries":["sample.exe","helper.exe"]}]'
    )

    results = parse_scoop_search(text)

    assert results == [
        ScoopSearchResult(
            name="sample-tool",
            version="",
            source="sample-bucket",
            binaries="sample.exe helper.exe",
        )
    ]


def test_parse_scoop_search_fallback_parses_formatted_table() -> None:
    text = (
        "\x1b[33mResults from local buckets...\x1b[0m\r\n"
        "Name  Version  Source  Binaries\r\n"
        "----  -------  ------  --------\r\n"
        "delta-tool  0.1.0  bucket-d  delta.exe\r\n"
        "epsilon-pack  0.2.0  bucket-e  epsilon.exe  epsilon-helper.exe\r\n"
    )

    results = parse_scoop_search(text)

    assert results == [
        ScoopSearchResult(
            name="delta-tool",
            version="0.1.0",
            source="bucket-d",
            binaries="delta.exe",
        ),
        ScoopSearchResult(
            name="epsilon-pack",
            version="0.2.0",
            source="bucket-e",
            binaries="epsilon.exe  epsilon-helper.exe",
        ),
    ]


def test_parse_scoop_search_fallback_supports_single_column_rows() -> None:
    results = parse_scoop_search("zeta-item")

    assert results == [ScoopSearchResult(name="zeta-item")]


def test_sanitize_normalizes_newlines_and_removes_ansi() -> None:
    text = "line1\r\nline2\r\x1b[31mline3\x1b[0m\x1b]0;title\x07"
    assert _sanitize(text) == "line1\nline2\nline3"
