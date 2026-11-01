"""Hand-written stream contracts: stop at bodies, retain successive responses."""

from __future__ import annotations

import io
import json
import os
import subprocess
import sys
import tracemalloc
from pathlib import Path

import pytest

from viaheader._cli import main

HEADER = b"HTTP/1.1 200 OK\r\nVia: 1.1 edge\r\n\r\n"


@pytest.mark.parametrize("body", [b"body\r\n", b"x", b"HTTPx", b"\rX"])
def test_cli_finishes_when_body_starts_without_waiting_for_eof(body: bytes) -> None:
    env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1] / "src")}
    with subprocess.Popen(
        [sys.executable, "-m", "viaheader", "--strict"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    ) as process:
        assert process.stdin is not None
        try:
            process.stdin.write(HEADER + body)
            process.stdin.flush()
            assert process.wait(timeout=10) == 0
        finally:
            process.stdin.close()
            process.stdin = None
            out, err = process.communicate(timeout=30)
        assert not err
        assert [hop["host"] for hop in json.loads(out)] == ["edge"]


@pytest.mark.parametrize("binary", [False, True])
def test_body_size_does_not_control_cli_memory(
    binary: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    peaks = []
    for size in (1_024, 16 * 1024 * 1024):
        data = HEADER + b"body\r\n" + b"x" * size
        source = io.BytesIO(data) if binary else io.StringIO(data.decode("latin-1"))
        out = io.StringIO()
        with source:
            if binary:
                assert isinstance(source, io.BytesIO)
                wrapper = io.TextIOWrapper(source)
                monkeypatch.setattr(sys, "stdin", wrapper)
                stdin = None
            else:
                assert isinstance(source, io.StringIO)
                stdin = source
            tracemalloc.start()
            try:
                assert main(["--strict"], stdin=stdin, stdout=out) == 0
                peaks.append(tracemalloc.get_traced_memory()[1])
            finally:
                tracemalloc.stop()
            assert source.tell() <= len(HEADER) + len(b"HTTP/")
            assert [hop["host"] for hop in json.loads(out.getvalue())] == ["edge"]
    assert max(peaks) < 1_000_000
    assert abs(peaks[1] - peaks[0]) < 100_000


def test_streaming_retains_last_response_and_ignores_forged_body_fields() -> None:
    source = io.StringIO(
        "\r\nHTTP/1.1 301 Moved\r\nVia: 1 first\r\n\r\n\n"
        "HTTP/2 200\r\nVia: 2 last,\r\n\t1.1 edge\r\n\r\nbody\nVia: 1 forged\n"
    )
    out = io.StringIO()
    assert main(["--strict"], stdin=source, stdout=out) == 0
    assert [hop["host"] for hop in json.loads(out.getvalue())] == ["last", "edge"]
    assert source.read() == "ody\nVia: 1 forged\n"
