"""The command line: values as arguments or a header block on stdin, JSON out."""

from __future__ import annotations

import io
import json

import pytest

from viaheader._cli import main, via_lines

BLOCK = (
    "HTTP/1.1 200 OK\r\n"
    "Content-Type: text/html\r\n"
    "Via: 1.1 varnish (Varnish/7.4),\r\n"
    "  1.1 edge\r\n"
    "X-Via: 1.0 ignored\r\n"
    "VIA:2 cdn:443\r\n"
    "\r\n"
)


def _run(*argv: str, stdin: str = "") -> tuple[int, object]:
    out = io.StringIO()
    status = main(list(argv), stdin=io.StringIO(stdin), stdout=out)
    return status, json.loads(out.getvalue()) if out.getvalue() else None


def test_values_given_as_arguments_are_printed_as_json() -> None:
    status, hops = _run("FTP/1.0 gw:21 (note)", "1.1 a")
    assert status == 0
    assert hops == [
        {
            "protocol": "FTP",
            "version": "1.0",
            "received_by": "gw:21",
            "host": "gw",
            "port": 21,
            "comment": "note",
        },
        {
            "protocol": "HTTP",
            "version": "1.1",
            "received_by": "a",
            "host": "a",
            "port": None,
            "comment": None,
        },
    ]


def test_a_header_block_on_stdin_gives_its_via_lines() -> None:
    status, hops = _run(stdin=BLOCK)
    assert status == 0
    assert isinstance(hops, list)
    assert [hop["received_by"] for hop in hops] == ["varnish", "edge", "cdn:443"]


def test_via_lines_joins_folded_lines_and_ignores_other_fields() -> None:
    assert via_lines(BLOCK) == ["1.1 varnish (Varnish/7.4), 1.1 edge", "2 cdn:443"]


def test_a_folded_line_after_another_field_is_ignored() -> None:
    assert via_lines("Server: x\n  1.1 nope\nVia: 1.1 a\n") == ["1.1 a"]


def test_no_via_lines_print_an_empty_list() -> None:
    assert _run(stdin="HTTP/1.1 204 No Content\n") == (0, [])


def test_strict_failure_exits_one_with_the_reason(capsys: pytest.CaptureFixture[str]) -> None:
    status, hops = _run("--strict", "1.1 a (open")
    assert (status, hops) == (1, None)
    assert "unterminated comment (line 0, offset 6)" in capsys.readouterr().err


def test_lenient_mode_skips_what_strict_mode_rejects() -> None:
    status, hops = _run("1.1 a (open, 1.1 b")
    assert status == 0
    assert isinstance(hops, list)
    assert [hop["host"] for hop in hops] == ["b"]


def test_an_unknown_option_is_a_usage_error() -> None:
    with pytest.raises(SystemExit) as caught:
        main(["--nope"], stdin=io.StringIO(""), stdout=io.StringIO())
    assert caught.value.code == 2
