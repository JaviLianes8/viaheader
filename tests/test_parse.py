"""Lenient parsing: what is read, what is skipped, and where reading resumes."""

from __future__ import annotations

import pytest

from viaheader import Hop, parse


def test_a_version_alone_means_http() -> None:
    assert parse("1.1 proxy") == [Hop(received_by="proxy", version="1.1")]


def test_an_explicit_protocol_name_is_kept() -> None:
    assert parse("FTP/1.0 gateway") == [Hop("gateway", "1.0", protocol="FTP")]


@pytest.mark.parametrize("name", ["HTTP", "http", "Http"])
def test_the_http_name_is_normalised_whatever_its_case(name: str) -> None:
    assert parse(f"{name}/1.1 GWA") == [Hop("GWA", "1.1")]


def test_received_by_may_carry_a_port() -> None:
    (hop,) = parse("1.0 proxy2:8080")
    assert (hop.received_by, hop.host, hop.port) == ("proxy2:8080", "proxy2", 8080)


def test_an_empty_port_is_allowed_and_reads_as_none() -> None:
    (hop,) = parse("1.1 proxy:")
    assert (hop.received_by, hop.host, hop.port) == ("proxy:", "proxy", None)


def test_a_comment_is_decoded() -> None:
    assert parse(r"1.1 p (a \) b \\ c)") == [Hop("p", "1.1", comment="a ) b \\ c")]


def test_nested_comments_stay_in_the_text() -> None:
    assert parse("1.1 p (one (two) three)")[0].comment == "one (two) three"


def test_an_empty_comment_is_an_empty_string() -> None:
    assert parse("1.1 p ()")[0].comment == ""


def test_a_comma_inside_a_comment_does_not_split() -> None:
    assert parse("1.1 proxy (one, two)") == [Hop("proxy", "1.1", comment="one, two")]


def test_multiple_hops_split_on_top_level_commas() -> None:
    assert parse("1.1 proxy1, 1.0 proxy2:8080 (edge)") == [
        Hop("proxy1", "1.1"),
        Hop("proxy2:8080", "1.0", comment="edge"),
    ]


def test_tabs_and_spaces_are_whitespace() -> None:
    assert parse("\t1.1\t\tp\t(c)\t,\t2 q ") == [Hop("p", "1.1", comment="c"), Hop("q", "2")]


def test_empty_elements_are_ignored() -> None:
    assert parse(" , ,1.1 a,, ,1.1 b, ") == [Hop("a", "1.1"), Hop("b", "1.1")]


def test_an_empty_value_has_no_hops() -> None:
    assert parse("") == [] and parse([]) == []


def test_each_field_line_is_its_own_list() -> None:
    assert parse(["1.0 a (open", "1.1 b"]) == [Hop("b", "1.1")]


def test_a_tuple_or_generator_of_lines_works() -> None:
    assert parse(line for line in ("1.0 a", "1.1 b")) == [Hop("a", "1.0"), Hop("b", "1.1")]


def test_a_comment_needs_no_space_before_it_when_lenient() -> None:
    assert parse("1.1 p(c)") == [Hop("p", "1.1", comment="c")]


def test_a_bracketed_ipv6_received_by_is_read_when_lenient() -> None:
    (hop,) = parse("1.1 [2001:db8::1]:8080")
    assert (hop.host, hop.port) == ("[2001:db8::1]", 8080)


@pytest.mark.parametrize("value", ["1.1 [2001:db8::1", "1.1 [nothex]", "1.1 [1.2.3.4]"])
def test_a_broken_ip_literal_is_skipped(value: str) -> None:
    assert parse(value + ", 1.1 b") == [Hop("b", "1.1")]


@pytest.mark.parametrize(
    "entry",
    [
        "1.1",
        "1.1 ",
        "garbage",
        "1.1 a b",
        "1.1 a (c) d",
        "1.1/ a",
        "/1.1 a",
        "a/b/c d",
        "1.1 a:x",
        "1.1 a/b",
        "1.1 (c)",
        "1.1 a (c",
        "1.1 a (c (d)",
        "1.1 a (\x01)",
        "1.1 a (" + chr(0x100) + ")",
        "1.1 a (c \\",
        "1.1 a (c \\\x01)",
        "1.1 a\x7f",
    ],
)
def test_an_invalid_entry_is_skipped_and_the_next_one_read(entry: str) -> None:
    assert parse(f"1.0 x, {entry}, 1.1 next") == [Hop("x", "1.0"), Hop("next", "1.1")]


@pytest.mark.parametrize("bad", ["\x01", "\\\x01", chr(0x100)])
def test_a_bad_character_in_a_comment_resumes_after_that_character(bad: str) -> None:
    assert parse(f"1.0 a (x, 1.1 b, {bad}), 1.1 c") == [Hop("c", "1.1")]


def test_an_unclosed_comment_cannot_swallow_the_entries_after_it() -> None:
    assert parse("1.0 client (, 1.1 edge") == [Hop("edge", "1.1")]


def test_reading_resumes_after_the_broken_point_not_inside_a_closed_comment() -> None:
    assert parse("1.1 a (x, 1.0 fake) junk, 1.1 b") == [Hop("b", "1.1")]


def test_an_escaped_comma_in_an_unclosed_comment_still_resynchronises() -> None:
    assert parse("1.0 c (x\\, 1.1 edge (y\\()") == [Hop("edge", "1.1", comment="y(")]


def test_cr_lf_and_nul_become_spaces_when_lenient() -> None:
    assert parse("1.1\r\n a (b\x00c)") == [Hop("a", "1.1", comment="b c")]


def test_latin_1_text_is_kept_in_a_comment() -> None:
    assert parse("1.1 a (caf\xe9)")[0].comment == "caf\xe9"


@pytest.mark.parametrize("value", [b"1.1 a", bytearray(b"1.1 a"), memoryview(b"1.1 a")])
def test_bytes_are_refused_with_a_clear_message(value: object) -> None:
    with pytest.raises(TypeError, match="latin-1"):
        parse(value)  # type: ignore[arg-type]


def test_a_line_that_is_not_a_string_is_refused() -> None:
    with pytest.raises(TypeError, match="int"):
        parse(["1.1 a", 5])  # type: ignore[list-item]


def test_a_missing_header_has_no_hops() -> None:
    assert parse(None) == []
