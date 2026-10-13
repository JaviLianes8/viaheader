"""How the command line reads a header block: bytes, line ends, blocks, terminals."""

from __future__ import annotations

import io
import json
import sys

import pytest

from viaheader._cli import main, via_lines


class _Stdin(io.TextIOWrapper):
    def __init__(self, data: bytes, tty: bool = False) -> None:
        super().__init__(io.BytesIO(data), encoding="utf-8")
        self._tty = tty

    def isatty(self) -> bool:
        return self._tty


def test_stdin_bytes_are_read_as_latin_1(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "stdin", _Stdin(b"Via: 1.1 a (caf\xe9 \x80)\r\n\r\n"))
    out = io.StringIO()
    assert main(["--strict"], stdout=out) == 0
    assert json.loads(out.getvalue())[0]["comment"] == "caf\xe9 \x80"


def test_a_terminal_on_stdin_is_a_usage_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "stdin", _Stdin(b"", tty=True))
    with pytest.raises(SystemExit) as caught:
        main([], stdout=io.StringIO(), stderr=io.StringIO())
    assert caught.value.code == 2


def test_errors_go_to_the_given_stream() -> None:
    err = io.StringIO()
    assert main(["--strict", "1.1 a b"], stdout=io.StringIO(), stderr=err) == 1
    assert err.getvalue().startswith("viaheader: unexpected 'b'")


@pytest.mark.parametrize("brk", ["\x0b", "\x0c", "\x1c", "\x1d", "\x1e", "\x85", "\r"])
def test_only_lf_ends_a_line(brk: str) -> None:
    assert via_lines(f"X-Foo: bar{brk}Via: 1.1 forged\r\n") == []
    assert via_lines(f"Via: 1.1 a (x{brk}y)\r\n") == [f"1.1 a (x{brk}y)"]


def test_the_body_after_the_blank_line_is_not_read() -> None:
    assert via_lines("HTTP/1.1 200 OK\r\nVia: 1.1 a\r\n\r\nVia: 1.1 body\r\n") == ["1.1 a"]


def test_the_last_response_of_a_redirect_chain_is_used() -> None:
    block = "HTTP/1.1 301 Moved\r\nVia: 1.1 first\r\n\r\nHTTP/2 200\r\nvia: 1.1 second\r\n\r\n"
    assert via_lines(block) == ["1.1 second"]


def test_leading_blank_lines_and_a_request_line_are_skipped() -> None:
    assert via_lines("\r\n\r\nGET http://a/ HTTP/1.1\r\nVia: 1.0 fred\r\n") == ["1.0 fred"]


def test_a_huge_port_prints_null() -> None:
    out = io.StringIO()
    assert main(["1.1 a:" + "9" * 5000], stdout=out) == 0
    assert json.loads(out.getvalue())[0]["port"] is None
