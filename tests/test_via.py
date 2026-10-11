from viaheader import Hop, build, parse


def test_single_hop_with_version_only_defaults_to_http() -> None:
    assert parse("1.1 proxy") == [Hop(received_by="proxy", version="1.1")]


def test_single_hop_keeps_an_explicit_protocol_name() -> None:
    assert parse("FTP/1.0 gateway") == [Hop(received_by="gateway", version="1.0", protocol="FTP")]


def test_received_by_may_carry_a_port() -> None:
    assert parse("1.0 proxy2:8080") == [Hop(received_by="proxy2:8080", version="1.0")]


def test_a_comment_is_captured_without_its_parentheses() -> None:
    assert parse("1.1 proxy (local cache)") == [
        Hop(received_by="proxy", version="1.1", comment="local cache")
    ]


def test_multiple_hops_split_on_top_level_commas() -> None:
    assert parse("1.1 proxy1, 1.0 proxy2:8080 (edge)") == [
        Hop(received_by="proxy1", version="1.1"),
        Hop(received_by="proxy2:8080", version="1.0", comment="edge"),
    ]


def test_a_comma_inside_a_comment_does_not_split_the_hop() -> None:
    assert parse("1.1 proxy (one, two)") == [
        Hop(received_by="proxy", version="1.1", comment="one, two")
    ]


def test_build_drops_the_http_name_and_wraps_the_comment() -> None:
    hops = [
        Hop(received_by="proxy1", version="1.1"),
        Hop(received_by="gw", version="1.0", protocol="FTP", comment="note"),
    ]
    assert build(hops) == "1.1 proxy1, FTP/1.0 gw (note)"


def test_parse_and_build_round_trip() -> None:
    header = "1.1 proxy1, FTP/1.0 proxy2:8080 (secret agent)"
    assert build(parse(header)) == header


def test_malformed_entries_are_skipped_without_raising() -> None:
    assert parse("garbage, 1.1 proxy, , 1.0") == [Hop(received_by="proxy", version="1.1")]


def test_an_empty_header_yields_no_hops() -> None:
    assert parse("") == []
