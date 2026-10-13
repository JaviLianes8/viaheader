"""Strict parsing: the RFC 9110 section 7.6.3 grammar, and the errors it raises."""

from __future__ import annotations

import re

import pytest

from viaheader import Hop, ViaError, parse


@pytest.mark.parametrize(
    "value",
    [
        "",
        "1.0 fred, 1.1 p.example.net",
        "HTTP/1.1 GWA",
        "FTP/1.0 gw:21 (note)",
        "1.1 p (a (b) \\) c)",
        "1.1 p:",
        "1.1 p:0080",
        " , 1.1 a ,, 1.1 b ,",
        "1.1\tp\t(c)",
        "2 !#$%&'*+-.^_`|~ (\xe9)",
    ],
)
def test_valid_values_pass(value: str) -> None:
    assert parse(value, strict=True) == parse(value)


@pytest.mark.parametrize(
    ("value", "position", "message"),
    [
        ("1.1", 3, "whitespace after the received-protocol"),
        ("1.1 ", 4, "received-by"),
        ("1.1 a b", 6, "unexpected 'b'"),
        ("1.1 p(c)", 5, "whitespace before the comment"),
        ("1.1 [::1]", 4, "received-by"),
        ("1.1 p (c", 6, "unterminated comment"),
        ("1.1 p (c \\", 6, "unterminated comment"),
        ("/1.1 p", 0, "protocol version"),
        ("HTTP/ p", 5, "after '/'"),
        ("1.1 a, 1.1 b c", 13, "unexpected 'c'"),
        ("1.1 a\r\n", 5, "'\\r'"),
        ("1.1 a (\x00)", 7, "'\\x00'"),
        ("1.1 a (" + chr(0x100) + ")", 7, repr(chr(0x100))),
        ("1.1 a\x7f", 5, "'\\x7f'"),
    ],
)
def test_invalid_values_raise_with_the_offset(value: str, position: int, message: str) -> None:
    with pytest.raises(ViaError, match=re.escape(message)) as caught:
        parse(value, strict=True)
    assert caught.value.position == position
    assert caught.value.line == 0
    assert f"(line 0, offset {position})" in str(caught.value)


def test_the_error_names_the_field_line() -> None:
    with pytest.raises(ViaError) as caught:
        parse(["1.1 a", "1.1 b (", "1.1 c"], strict=True)
    assert (caught.value.line, caught.value.position) == (1, 6)


def test_via_error_is_a_value_error() -> None:
    assert issubclass(ViaError, ValueError)


def test_strict_and_lenient_agree_on_a_multi_line_value() -> None:
    lines = ["1.0 ricky, 1.1 ethel", "1.1 fred, 1.0 lucy"]
    assert parse(lines, strict=True) == [
        Hop("ricky", "1.0"),
        Hop("ethel", "1.1"),
        Hop("fred", "1.1"),
        Hop("lucy", "1.0"),
    ]
