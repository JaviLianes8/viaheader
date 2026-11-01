"""Validation messages remain small and do not quote rejected fields."""

from __future__ import annotations

import errno
import io
import sys
from collections.abc import Callable

import pytest

from viaheader import Hop, ViaError, append, build, has_loop, parse
from viaheader._cli import main, via_lines


@pytest.mark.parametrize("size", [1, 1_000_000])
def test_invalid_fields_are_not_echoed(size: int) -> None:
    secret = "private-value" * size
    calls: list[Callable[[], object]] = [
        lambda: build([Hop(secret + " ", "1")]),
        lambda: build([Hop("p", secret + " ")]),
        lambda: build([Hop("p", "1", secret + " ")]),
        lambda: append(None, Hop("p", "1"), pseudonyms={"p": secret + " "}),
        lambda: append(None, Hop("p", "1"), pseudonyms={secret + " ": "p"}),
        lambda: has_loop(None, secret + " "),
        lambda: has_loop(None, "p:" + "9" * size * 10),
    ]
    for call in calls:
        with pytest.raises(ViaError) as caught:
            call()
        assert "private-value" not in str(caught.value)
        assert len(str(caught.value)) < 100
        assert caught.value.line is None and caught.value.position is None


def test_strict_failure_never_echoes_the_whole_field() -> None:
    secret = "private-value" * 100_000
    with pytest.raises(ViaError) as caught:
        parse("1 " + secret + "\n", strict=True)
    assert len(str(caught.value)) < 100
    assert "private-value" not in str(caught.value)
    assert caught.value.position == 2 + len(secret)


def test_wrong_types_do_not_invoke_their_representation() -> None:
    class Unprintable:
        def __repr__(self) -> str:
            raise AssertionError("must not format a rejected object")

    value = Unprintable()
    with pytest.raises(TypeError):
        build([value])  # type: ignore[list-item]
    with pytest.raises(TypeError):
        parse([value])  # type: ignore[list-item]
    with pytest.raises(TypeError):
        has_loop(None, value)  # type: ignore[arg-type]


@pytest.mark.parametrize("value", [0, False, "", "p", [], [("p", "fw")]])
def test_pseudonyms_requires_a_mapping(value: object) -> None:
    with pytest.raises(TypeError, match="mapping"):
        append(None, Hop("me", "1"), pseudonyms=value)  # type: ignore[arg-type]


def test_unknown_options_are_not_echoed(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as caught:
        main(["--private-value" + "x" * 100_000])
    assert caught.value.code == 2
    error = capsys.readouterr().err
    assert "private-value" not in error and len(error) < 300
    assert "unrecognized arguments" in error


@pytest.mark.parametrize("option", ["--strict", "--help", "-h"])
def test_unexpected_option_values_are_not_echoed(
    option: str, capsys: pytest.CaptureFixture[str]
) -> None:
    with pytest.raises(SystemExit) as caught:
        main([option + "=private-value" + "x" * 100_000])
    assert caught.value.code == 2
    error = capsys.readouterr().err
    assert "private-value" not in error and len(error) < 300
    assert "does not accept a value" in error


def test_closed_output_returns_one_without_a_traceback(monkeypatch: pytest.MonkeyPatch) -> None:
    class Closed(io.StringIO):
        def write(self, text: str) -> int:
            raise BrokenPipeError

    monkeypatch.setattr(sys, "stdout", Closed())
    assert main(["1 p"]) == 1
    sys.stdout.flush()


def test_other_output_errors_propagate() -> None:
    class Failed(io.StringIO):
        def flush(self) -> None:
            raise OSError(errno.ENOSPC, "storage full")

    with pytest.raises(OSError) as caught:
        main(["1 p"], stdout=Failed())
    assert caught.value.errno == errno.ENOSPC


def test_folded_header_values_keep_all_fragments() -> None:
    assert via_lines("Via: 1 p (\n" + " x\n" * 40_000 + " )\n") == ["1 p (" + " x" * 40_000 + " )"]


def test_many_proxy_names_do_not_require_a_cartesian_scan() -> None:
    value = ",".join(f"1 p{n}" for n in range(20_000))
    names = [f"other{n}" for n in range(20_000)]
    assert not has_loop(value, *names)
    assert has_loop(value, *names, "p19999")
