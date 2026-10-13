"""Build the wheel, install it in a throwaway venv and drive the installed package.

Slow and needs the build backend, so it runs only with VIAHEADER_E2E=1.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import venv
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

pytestmark = pytest.mark.skipif(
    os.environ.get("VIAHEADER_E2E") != "1", reason="set VIAHEADER_E2E=1 to build and install"
)

PROGRAM = r"""
import importlib.metadata, importlib.resources, pickle
import viaheader
from viaheader import Hop, ViaError, append, build, has_loop, parse

assert "site-packages" in viaheader.__file__, viaheader.__file__
assert importlib.metadata.version("viaheader") == viaheader.__version__
assert importlib.resources.files("viaheader").joinpath("py.typed").is_file()

assert parse("1.0 client (, 1.1 edge:8080") == [Hop("edge:8080", "1.1")]
assert has_loop(["1.0 client (", "1.1 Edge:8080"], "edge")
assert append("1.1 lb.corp (squid), 1.0 x (", Hop("me", "2"), pseudonyms={"LB.corp": "lb"}) == (
    "1.1 lb (squid), 2 me"
)
hop = Hop("gw:21", "1.0", protocol="FTP", comment="a ) (b) \\")
value = build([hop])
assert value == "FTP/1.0 gw:21 (a \\) (b) \\\\)", value
assert parse(value, strict=True) == [hop] and (hop.host, hop.port) == ("gw", 21)
assert pickle.loads(pickle.dumps(hop)) == hop
for call in (
    lambda: parse("1.1 a b", strict=True),
    lambda: build([Hop("p\r\nX-Admin: 1", "1.1")]),
    lambda: has_loop("1.1 a", "a b"),
):
    try:
        call()
    except ViaError as error:
        assert isinstance(error, ValueError)
    else:
        raise AssertionError("expected ViaError")
print("e2e ok")
"""


def _run(
    *cmd: str | Path, cwd: Path | None = None, stdin: bytes = b""
) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        [str(c) for c in cmd], cwd=cwd, input=stdin, capture_output=True, check=False
    )


def test_installed_wheel_end_to_end(tmp_path: Path) -> None:
    dist = tmp_path / "dist"
    built = _run(sys.executable, "-m", "build", "--outdir", dist, ROOT)
    assert built.returncode == 0, built.stderr
    (wheel,) = dist.glob("viaheader-*.whl")
    (sdist,) = dist.glob("viaheader-*.tar.gz")
    names = zipfile.ZipFile(wheel).namelist()
    assert "viaheader/py.typed" in names
    assert "viaheader/__main__.py" in names
    assert not any(name.startswith(("tests/", "scripts/", "scratchpad/")) for name in names)
    listing = _run(sys.executable, "-m", "tarfile", "-l", sdist).stdout.decode()
    assert "IMPROVEMENTS-round" not in listing
    assert "scratchpad" not in listing
    assert "tests/upstream/MANIFEST.json" in listing
    for fetched in ("rfc9110.txt", "rfc9112.txt", "rfc3986.txt", "mdn-via.md"):
        assert fetched not in listing, fetched
    assert "tests/test_sources.py" in listing
    assert "scripts/fetch_upstream.py" in listing

    env_dir = tmp_path / "venv"
    venv.create(env_dir, with_pip=True)
    bindir = env_dir / ("Scripts" if sys.platform == "win32" else "bin")
    python = bindir / "python"
    installed = _run(python, "-m", "pip", "install", "-q", wheel)
    assert installed.returncode == 0, installed.stderr

    # Run from an empty folder so the source tree cannot shadow the install.
    work = tmp_path / "work"
    work.mkdir()
    result = _run(python, "-I", "-c", PROGRAM, cwd=work)
    assert result.returncode == 0, result.stderr
    assert result.stdout.decode().strip() == "e2e ok"

    block = b"HTTP/1.1 200 OK\r\nVia: 1.1 varnish (Varnish/7.4)\r\nvia: 2 cdn:443\r\n\r\n"
    for command in ([python, "-I", "-m", "viaheader"], [bindir / "viaheader"]):
        shown = _run(*command, cwd=work, stdin=block)
        assert shown.returncode == 0, shown.stderr
        assert [hop["host"] for hop in json.loads(shown.stdout)] == ["varnish", "cdn"]
    rejected = _run(bindir / "viaheader", "--strict", "1.1 a (", cwd=work)
    assert rejected.returncode == 1
    assert b"unterminated comment" in rejected.stderr
