"""Hand-written contracts for the underlying text of string subclasses."""

from __future__ import annotations

from collections.abc import Iterator
from typing import SupportsIndex

import pytest

from viaheader import Hop, ViaError, append, build, has_loop, parse


class Mask(str):
    def __iter__(self) -> Iterator[str]:
        return iter("safe")

    def __str__(self) -> str:
        return "decoy"


class Long(str):
    def __len__(self) -> int:
        return 100


class Whole(str):
    def __getitem__(self, key: SupportsIndex | slice) -> str:
        return self


class DisguisedProtocol(str):
    def upper(self) -> str:
        return "HTTP"


@pytest.mark.parametrize("field", ["received_by", "version", "protocol", "comment"])
@pytest.mark.parametrize("forward", [False, True])
def test_serialization_rejects_hidden_injection(field: str, forward: bool) -> None:
    fields = {"received_by": "edge", "version": "1.1", field: Mask("v\r\nX-Injected: yes")}
    hop = Hop(**fields)
    with pytest.raises(ViaError):
        append(None, hop) if forward else build([hop])


def test_protocol_normalization_uses_underlying_text() -> None:
    with pytest.raises(ViaError):
        build([Hop("edge", "1.1", DisguisedProtocol("bad\nprotocol"))])


def test_hop_fields_preserve_underlying_string_values() -> None:
    hop = Hop(Mask("edge:443"), Mask("1.1"), Mask("FTP"), Mask("cache"))
    assert (hop.host, hop.port) == ("edge", 443)
    assert build([hop]) == "FTP/1.1 edge:443 (cache)"
    assert parse(build([hop]), strict=True) == [hop]
    assert all(
        type(value) is str for value in (hop.received_by, hop.version, hop.protocol, hop.comment)
    )


@pytest.mark.parametrize("wrapped", [False, True])
@pytest.mark.parametrize("strict", [False, True])
@pytest.mark.parametrize("kind", [Mask, Long, Whole])
def test_parse_uses_underlying_field_line(kind: type[str], strict: bool, wrapped: bool) -> None:
    value = kind("1.1 edge")
    assert parse([value] if wrapped else value, strict=strict) == [Hop("edge", "1.1")]


@pytest.mark.parametrize("wrapped", [False, True])
def test_invalid_character_error_does_not_echo_subclass_input(wrapped: bool) -> None:
    value = Whole("\x01PRIVATE_TOKEN_72eac01f" + "q" * 100_000)
    with pytest.raises(ViaError) as caught:
        parse(["1.1 first", value] if wrapped else value, strict=True)
    assert (caught.value.line, caught.value.position) == (int(wrapped), 0)
    assert str(caught.value) == f"invalid character '\\x01' (line {int(wrapped)}, offset 0)"


@pytest.mark.parametrize("used", [False, True])
def test_invalid_subclass_pseudonym_is_rejected_even_when_unused(used: bool) -> None:
    with pytest.raises(ViaError):
        append("1.1 edge" if used else None, Hop("me", "1.1"), pseudonyms={"edge": Mask("bad\n")})


def test_pseudonym_and_loop_names_use_underlying_text() -> None:
    assert append("1.1 EDGE", Hop("me", "1.1"), pseudonyms={Mask("edge"): Mask("fw")}) == (
        "1.1 fw, 1.1 me"
    )
    assert has_loop("1.1 edge:443", Long("edge:443"))


def test_inert_subclasses_remain_accepted() -> None:
    class Text(str):
        pass

    hop = Hop(Text("edge"), Text("1.1"), Text("http"), Text("\t"))
    assert parse(Text(build([hop])), strict=True) == [hop]


@pytest.mark.parametrize("name", ["edge", "edge:"])
def test_subclass_proxy_names_without_a_port_use_underlying_length(name: str) -> None:
    assert has_loop("1.1 edge:443", Long(name))
    assert not has_loop("1.1 other:443", Long(name))
