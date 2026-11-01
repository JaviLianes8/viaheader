"""Seeded external-consumer snapshot, executed separately on 0.2.0 and the new wheel."""

from __future__ import annotations

import json
import random
from collections.abc import Callable
from dataclasses import asdict

from viaheader import Hop, ViaError, append, build, has_loop, parse


def snapshot() -> list[object]:
    rng = random.Random(1009110)
    result: list[object] = []
    alphabet = "ab01/.:;[]() ,\\\t\r\n\x00\x7f\xe9\u0100"
    for _ in range(5000):
        value = "".join(rng.choices(alphabet, k=rng.randrange(40)))
        value += rng.choice(["", ", 1.1 Edge:80", ", 2 [::1] (cache)"])
        for strict in (False, True):
            try:
                result.append([asdict(h) for h in parse(value, strict=strict)])
            except ViaError as error:
                result.append(["ViaError", error.line, error.position])
        hop = Hop("edge", "2", comment=rng.choice([None, "", ") (", "caf\xe9\\"]))
        result.extend([build([hop]), append(value, hop), has_loop(value, "edge:80", "[::1]")])
    calls: list[Callable[[], object]] = [
        lambda: build([Hop("private value", "1")]),
        lambda: build([Hop("p", "private value")]),
        lambda: build([Hop("p", "1", "private value")]),
        lambda: append(None, Hop("me", "1"), pseudonyms={"p": "private value"}),
        lambda: append(None, Hop("me", "1"), pseudonyms={"private value": "p"}),
        lambda: has_loop(None, "private value"),
        lambda: has_loop(None, "p:65536"),
    ]
    for call in calls:
        try:
            call()
        except ViaError as error:
            result.append(["ViaError", error.line, error.position])
        else:
            raise AssertionError("expected a validation error")
    return result


if __name__ == "__main__":
    print(json.dumps(snapshot(), sort_keys=True))
