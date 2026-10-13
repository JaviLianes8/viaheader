"""Seeded random checks of the two promises that matter most.

1. Whatever a client writes, the entries proxies append after it parse unchanged.
2. Whatever the lenient parser returns, append writes back and strict parsing reads.
"""

from __future__ import annotations

import random

from viaheader import Hop, append, build, has_loop, parse

# Characters chosen to stress the scanner: structure, escapes, controls, latin-1, wide.
ALPHABET = 'abc19./:;[]() ,\\\t\r\n\x00\x7f\xe9"=_' + chr(0x100)
SEED_COUNT = 3000


def _noise(rng: random.Random) -> str:
    return "".join(rng.choice(ALPHABET) for _ in range(rng.randrange(0, 24)))


def _comment(rng: random.Random) -> str | None:
    if rng.random() < 0.4:
        return None
    return "".join(rng.choice("ab (),\\\t\xe9") for _ in range(rng.randrange(0, 10)))


def _hop(rng: random.Random) -> Hop:
    received_by = rng.choice(["edge", "p.example.net", "fw1", "lb"]) + rng.choice(["", ":80", ":"])
    protocol = rng.choice(["HTTP", "FTP", "h2c"])
    return Hop(received_by, rng.choice(["1.0", "1.1", "2"]), protocol, _comment(rng))


def test_a_client_prefix_never_changes_the_appended_entries() -> None:
    rng = random.Random(9110)
    for _ in range(SEED_COUNT):
        trusted = [_hop(rng) for _ in range(rng.randrange(1, 4))]
        suffix = build(trusted)
        prefix = _noise(rng)
        for value in (f"{prefix}, {suffix}", f"{prefix},{suffix}", [prefix, suffix]):
            hops = parse(value)
            assert hops[len(hops) - len(trusted) :] == trusted, (prefix, suffix)


def test_a_client_prefix_cannot_hide_a_loop() -> None:
    rng = random.Random(7230)
    for _ in range(SEED_COUNT):
        assert has_loop(f"{_noise(rng)}, 1.1 edge:8080 (x)", "edge"), "loop hidden"


def test_lenient_results_survive_append_and_strict_parsing() -> None:
    rng = random.Random(9112)
    me = Hop("me", "1.1")
    for _ in range(SEED_COUNT):
        received = ", ".join(_noise(rng) for _ in range(3))
        hops = parse(received)
        forwarded = append(received, me)
        assert parse(forwarded) == [*hops, me]
        # Entries received in the RFC 7230 IP-literal form are kept, and only they are not
        # RFC 9110 syntax.
        if not any(hop.received_by.startswith("[") for hop in hops):
            assert parse(forwarded, strict=True) == [*hops, me]


def test_build_then_parse_is_the_identity() -> None:
    rng = random.Random(3986)
    for _ in range(SEED_COUNT):
        hops = [_hop(rng) for _ in range(rng.randrange(0, 4))]
        assert parse(build(hops), strict=True) == hops
