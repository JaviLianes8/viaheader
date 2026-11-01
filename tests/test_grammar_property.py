"""A bounded reference grammar derived from the fetched RFC, not from parser code."""

from __future__ import annotations

import random
import re

import pytest
from test_sources import _codes, _rule

from viaheader import ViaError, parse


def _character_class(codes: set[int]) -> str:
    return "[" + "".join(re.escape(chr(c)) for c in sorted(codes)) + "]"


def _grammar(rfc: str) -> re.Pattern[str]:
    token = _character_class(_codes(_rule(rfc, "tchar"))) + "+"
    ctext = _character_class(_codes(_rule(rfc, "ctext")))
    quoted = r"\\" + _character_class(_codes(_rule(rfc, "quoted-pair").removeprefix('"\\"')))
    assert _rule(rfc, "RWS") == "1*( SP / HTAB )"
    assert _rule(rfc, "OWS") == "*( SP / HTAB )"
    comment = rf"\((?:{ctext}|{quoted})*\)"
    for _ in range(3):
        comment = rf"\((?:{ctext}|{quoted}|{comment})*\)"
    entry = rf"(?:{token}/)?{token}[ \t]+{token}(?::[0-9]*)?(?:[ \t]+{comment})?"
    # The recipient list rule ignores empty members; the generated comments have
    # at most four nesting levels, so a regular expression is sufficient here.
    return re.compile(rf"[ \t]*(?:{entry})?(?:[ \t]*,[ \t]*(?:{entry})?)*[ \t]*")


@pytest.mark.parametrize("seed", [9110, 10000, 20261101])
def test_strict_parser_agrees_with_reference_grammar(rfc9110: str, seed: int) -> None:
    grammar = _grammar(rfc9110)
    rng = random.Random(seed)
    alphabet = "abc19: /()[]\\\t\r\n\x00\x7f\xe9\u0100\ud800"
    for index in range(10_000):
        if index % 2:
            value = "".join(rng.choices(alphabet, k=rng.randrange(0, 35)))
            # Arbitrary noise is bounded below the reference's nesting depth.
            if value.count("(") > 4:
                continue
        else:
            value = rng.choice(["1.1", "HTTP/2", "!/$", "ftp/1"])
            value += rng.choice([" ", "\t", "  "]) + rng.choice(["p", "x:0", "a:", "a:999999"])
            value += rng.choice(["", " ()", " ((x))", r" (a\)b)", " (caf\xe9)"])
            value = rng.choice(["", " ,", "1 a, "]) + value + rng.choice(["", ",", ", 2 b"])
            if rng.random() < 0.5:
                at = rng.randrange(len(value))
                value = value[:at] + rng.choice(alphabet) + value[at + 1 :]
        expected = grammar.fullmatch(value) is not None
        try:
            parse(value, strict=True)
        except ViaError as error:
            assert not expected, repr(value)
            assert error.line == 0
            assert error.position is not None and 0 <= error.position <= len(value)
            assert len(str(error)) < 150
        else:
            assert expected, repr(value)
