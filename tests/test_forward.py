"""append and has_loop: what a proxy does with the Via it received."""

from __future__ import annotations

import pytest

from viaheader import Hop, ViaError, append, has_loop, parse

ME = Hop("edge", "1.1")


def test_append_to_a_missing_header() -> None:
    assert append(None, ME) == "1.1 edge"


def test_append_to_an_empty_header() -> None:
    assert append("", ME) == append([], ME) == "1.1 edge"


def test_append_keeps_the_received_order() -> None:
    assert append("1.0 fred, 1.1 p.example.net", ME) == "1.0 fred, 1.1 p.example.net, 1.1 edge"


def test_append_reads_every_field_line() -> None:
    assert append(["1.0 a", "1.1 b (c)"], ME) == "1.0 a, 1.1 b (c), 1.1 edge"


def test_append_drops_an_entry_that_cannot_be_read() -> None:
    assert append("1.0 client (, 1.1 lb", ME) == "1.1 lb, 1.1 edge"


def test_an_unclosed_comment_cannot_swallow_the_new_entry() -> None:
    value = append("1.0 client (open", ME)
    assert parse(value, strict=True)[-1] == ME


def test_append_writes_received_entries_back_in_canonical_form() -> None:
    assert append("HTTP/1.1  GWA(note)", ME) == "1.1 GWA (note), 1.1 edge"


def test_append_keeps_a_legacy_ipv6_entry() -> None:
    assert append("1.1 [2001:db8::1]:80", ME) == "1.1 [2001:db8::1]:80, 1.1 edge"


def test_append_validates_its_own_entry() -> None:
    with pytest.raises(ViaError, match="received-by"):
        append("1.0 a", Hop("edge\r\nX-Admin: 1", "1.1"))
    with pytest.raises(ViaError, match="received-by"):
        append("1.0 a", Hop("[::1]", "1.1"))


def test_pseudonyms_replace_the_whole_received_by() -> None:
    value = append(
        "1.1 Internal.corp:8080 (squid), 1.0 public", ME, pseudonyms={"internal.CORP": "fw1"}
    )
    assert value == "1.1 fw1 (squid), 1.0 public, 1.1 edge"


def test_pseudonyms_match_a_legacy_ipv6_host() -> None:
    assert append("1.1 [::1]:80", ME, pseudonyms={"[::1]": "lo"}) == "1.1 lo, 1.1 edge"


def test_an_invalid_pseudonym_is_refused() -> None:
    with pytest.raises(ViaError, match="pseudonym"):
        append("1.1 a", ME, pseudonyms={"a": "b c"})


def test_pseudonyms_must_be_strings() -> None:
    with pytest.raises(TypeError, match="pseudonyms"):
        append("1.1 a", ME, pseudonyms={"a": 5})  # type: ignore[dict-item]
    with pytest.raises(TypeError, match="pseudonyms"):
        append("1.1 a", ME, pseudonyms={5: "a"})  # type: ignore[dict-item]


def test_drop_comments_removes_received_comments_only() -> None:
    value = append("1.1 a (x), 1.0 b (y)", Hop("edge", "1.1", comment="mine"), drop_comments=True)
    assert value == "1.1 a, 1.0 b, 1.1 edge (mine)"


def test_has_loop_finds_its_own_name() -> None:
    assert has_loop("1.0 fred, 1.1 edge (v1)", "edge")
    assert not has_loop("1.0 fred, 1.1 p.example.net", "edge")


def test_has_loop_ignores_case() -> None:
    assert has_loop("1.1 Edge.Example.NET", "edge.example.net")


def test_a_name_without_a_port_matches_any_port() -> None:
    assert has_loop("1.1 edge:8080", "edge")


def test_a_name_with_a_port_matches_only_that_port() -> None:
    assert has_loop("1.1 edge:8080", "edge:8080")
    assert not has_loop("1.1 edge:8081", "edge:8080")
    assert not has_loop("1.1 edge", "edge:8080")


def test_any_of_several_names_matches() -> None:
    assert has_loop("1.1 b", "a", "b")


def test_has_loop_reads_the_entries_a_client_tried_to_hide() -> None:
    assert has_loop("1.0 client (, 1.1 edge", "edge")
    assert has_loop(["1.0 client (", "1.1 edge"], "edge")


def test_has_loop_on_a_missing_header() -> None:
    assert not has_loop(None, "edge")


def test_has_loop_reads_a_legacy_ipv6_entry() -> None:
    assert has_loop("1.1 [2001:DB8::1]:80", "[2001:db8::1]")


@pytest.mark.parametrize(
    "name", ["", "a b", "edge:x", "edge:80:1", "[nope]", "a,b", "[fe80::1%eth0]", "[::1]x"]
)
def test_an_invalid_name_is_refused(name: str) -> None:
    with pytest.raises(ViaError, match="proxy name"):
        has_loop("1.1 edge", name)


def test_a_name_that_is_not_a_string_is_a_type_error() -> None:
    with pytest.raises(TypeError, match="str"):
        has_loop("1.1 edge", 5)  # type: ignore[arg-type]
