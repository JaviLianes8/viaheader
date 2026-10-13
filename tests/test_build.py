"""Building: valid output only, comments escaped, and parse(build(hops)) == hops."""

from __future__ import annotations

import pytest

from viaheader import Hop, ViaError, build, parse


def test_build_drops_the_http_name_and_wraps_the_comment() -> None:
    hops = [Hop("proxy1", "1.1"), Hop("gw", "1.0", protocol="FTP", comment="note")]
    assert build(hops) == "1.1 proxy1, FTP/1.0 gw (note)"


@pytest.mark.parametrize("protocol", ["HTTP", "http", ""])
def test_any_spelling_of_http_is_omitted(protocol: str) -> None:
    assert build([Hop("p", "2", protocol=protocol)]) == "2 p"


@pytest.mark.parametrize("protocol", ["http", "Http", ""])
def test_any_spelling_of_http_round_trips(protocol: str) -> None:
    hop = Hop("p", "1.1", protocol=protocol)
    assert hop.protocol == "HTTP" and hop == Hop("p", "1.1")
    assert parse(build([hop]), strict=True) == [hop]


def test_no_hops_build_an_empty_value() -> None:
    assert build([]) == ""


def test_a_round_trip_keeps_the_text() -> None:
    value = "1.1 proxy1, FTP/1.0 proxy2:8080 (secret agent)"
    assert build(parse(value)) == value


@pytest.mark.parametrize(
    ("comment", "written"),
    [
        ("plain", "(plain)"),
        ("", "()"),
        ("a (b) c", "(a (b) c)"),
        ("x), 1.1 forged (y", "(x\\), 1.1 forged \\(y)"),
        (")(", "(\\)\\()"),
        ("((a)", "(\\((a))"),
        ("back\\slash", "(back\\\\slash)"),
        ("tab\tand caf\xe9", "(tab\tand caf\xe9)"),
    ],
)
def test_comments_are_escaped_only_where_needed(comment: str, written: str) -> None:
    value = build([Hop("p", "1.1", comment=comment)])
    assert value == f"1.1 p {written}"
    assert parse(value, strict=True) == [Hop("p", "1.1", comment=comment)]


@pytest.mark.parametrize("comment", ["a\r\nX-Admin: 1", "nul\x00", "del\x7f", "\u0100", "\x1b"])
def test_a_comment_a_field_value_cannot_carry_is_refused(comment: str) -> None:
    with pytest.raises(ViaError, match="cannot carry"):
        build([Hop("p", "1.1", comment=comment)])


@pytest.mark.parametrize(
    "received_by",
    ["", "p\r\nX-Admin: 1", "a b", "a,b", "p:x", "p:1:2", ":80", "[::1]", "[::1]:80", "a(b"],
)
def test_an_invalid_received_by_is_refused(received_by: str) -> None:
    with pytest.raises(ViaError, match="received-by"):
        build([Hop(received_by, "1.1")])


@pytest.mark.parametrize("version", ["", "1 1", "1,1", "1/1", "1.1\n"])
def test_an_invalid_version_is_refused(version: str) -> None:
    with pytest.raises(ViaError, match="protocol version"):
        build([Hop("p", version)])


@pytest.mark.parametrize("protocol", ["a b", "a/b", "(x)", "\u0100"])
def test_an_invalid_protocol_name_is_refused(protocol: str) -> None:
    with pytest.raises(ViaError, match="protocol name"):
        build([Hop("p", "1.1", protocol=protocol)])


def test_valid_received_by_forms_are_written() -> None:
    assert (
        build([Hop("p:", "1"), Hop("p:0", "1"), Hop("~a.b-c_d", "1")]) == "1 p:, 1 p:0, 1 ~a.b-c_d"
    )


@pytest.mark.parametrize(
    "hop",
    [Hop(1, "1.1"), Hop("p", 1.1), Hop("p", "1.1", protocol=None), Hop("p", "1.1", comment=5)],  # type: ignore[arg-type]
)
def test_fields_that_are_not_strings_are_a_type_error(hop: Hop) -> None:
    with pytest.raises(TypeError):
        build([hop])


def test_something_that_is_not_a_hop_is_a_type_error() -> None:
    with pytest.raises(TypeError, match="Hop"):
        build(["1.1 p"])  # type: ignore[list-item]


def test_build_errors_have_no_position() -> None:
    with pytest.raises(ViaError) as caught:
        build([Hop("", "1.1")])
    assert caught.value.line is None and caught.value.position is None


def test_hop_host_and_port_for_hand_built_values() -> None:
    assert (Hop("[::1", "1").host, Hop("[::1", "1").port) == ("[::1", None)
    assert (Hop("a:b", "1").host, Hop("a:b", "1").port) == ("a", None)
    assert Hop("a:" + chr(0x663), "1").port is None
    assert Hop("[::1]x80", "1").port is None
    assert (Hop("[::1]:9", "1").host, Hop("[::1]:9", "1").port) == ("[::1]", 9)
