"""Client-sized input stays cheap: linear time, no unbounded integer conversion."""

from __future__ import annotations

import time
from collections.abc import Callable

import pytest

from viaheader import Hop, ViaError, append, has_loop, parse

SIZE = 256 * 1024
# Linear parsing takes well under a second here; the quadratic scan this guards against
# needed 47 s for 72 KB of the first pattern.
BUDGET = 3.0


def _timed(call: Callable[[], object]) -> float:
    start = time.perf_counter()
    call()
    return time.perf_counter() - start


@pytest.mark.parametrize(
    "unit",
    ["1 a (,", "1 a ((,", "(", ",", "1 a (x) b,", "1 a (\\,", "1 [::1", "1 a (\x01,", " ,"],
)
def test_hostile_values_parse_in_linear_time(unit: str) -> None:
    value = unit * (SIZE // len(unit)) + ", 1.1 edge"
    assert _timed(lambda: has_loop(value, "edge")) < BUDGET
    assert _timed(lambda: append(value, Hop("me", "1.1"))) < BUDGET
    assert parse(value)[-1] == Hop("edge", "1.1")


def test_deeply_nested_comments_parse_in_linear_time() -> None:
    depth = SIZE // 2
    value = "1.1 a " + "(" * depth + ")" * depth + ", 1.1 b"
    assert _timed(lambda: parse(value)) < BUDGET
    assert [hop.received_by for hop in parse(value)] == ["a", "b"]


def test_many_matched_comments_parse_in_linear_time() -> None:
    value = ", ".join(["1.1 a (x (y) z)"] * (SIZE // 16))
    assert _timed(lambda: parse(value, strict=True)) < BUDGET


def test_a_huge_port_does_not_break_loop_detection() -> None:
    value = "1.1 p:" + "9" * 5000
    assert not has_loop(value, "p:80")
    assert has_loop(value, "p")
    assert parse(value)[0].port is None


def test_a_port_with_many_leading_zeros_is_read() -> None:
    assert Hop("p:" + "0" * 5000 + "80", "1").port == 80


@pytest.mark.parametrize(
    ("received_by", "port"),
    [("p:", None), ("p:0", 0), ("p:65535", 65535), ("p:65536", None), ("p:099999", None)],
)
def test_ports_are_tcp_port_numbers(received_by: str, port: int | None) -> None:
    assert Hop(received_by, "1").port == port


def test_a_name_with_a_port_above_65535_is_refused() -> None:
    with pytest.raises(ViaError, match="65535"):
        has_loop("1.1 p", "p:" + "9" * 5000)
