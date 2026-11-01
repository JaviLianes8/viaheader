"""Hand-written contracts for whitespace and field association in folded headers."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def _strict_cli(block: bytes) -> subprocess.CompletedProcess[bytes]:
    env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1] / "src")}
    return subprocess.run(
        [sys.executable, "-m", "viaheader", "--strict"],
        input=block,
        capture_output=True,
        env=env,
        timeout=30,
        check=False,
    )


def test_initial_field_rejects_trailing_nonbreaking_space() -> None:
    result = _strict_cli(b"Via: 1.1 edge\xa0\r\n\r\n")
    assert result.returncode == 1
    assert result.stdout == b""
    assert result.stderr.startswith(b"viaheader: ")


def test_folded_comment_preserves_trailing_nonbreaking_space() -> None:
    result = _strict_cli(b"Via: 1.1 edge (\r\n x\xa0\r\n )\r\n\r\n")
    assert result.returncode == 0, result.stderr
    assert result.stderr == b""
    assert json.loads(result.stdout)[0]["comment"] == " x\u00a0 "


def test_folded_comment_preserves_internal_tab() -> None:
    result = _strict_cli(b"Via: 1.1 edge (\r\n x\ty)\r\n\r\n")
    assert result.returncode == 0, result.stderr
    assert result.stderr == b""
    assert json.loads(result.stdout)[0]["comment"] == " x\ty"


def test_continuation_belongs_to_second_via_field() -> None:
    result = _strict_cli(b"Via: 1.1 first\r\nVia: 1.1 second\r\n (note)\r\n\r\n")
    assert result.returncode == 0, result.stderr
    assert result.stderr == b""
    assert [(hop["host"], hop["comment"]) for hop in json.loads(result.stdout)] == [
        ("first", None),
        ("second", "note"),
    ]
