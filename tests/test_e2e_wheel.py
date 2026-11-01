"""Build the wheel, install it in a throwaway venv and drive the installed package.

Slow and needs the build backend, so it runs only with VIAHEADER_E2E=1.
"""

from __future__ import annotations

import json
import os
import pickle
import subprocess
import sys
import tarfile
import venv
import zipfile
from email.parser import BytesParser
from pathlib import Path

import pytest

from viaheader import Hop, ViaError

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
        [str(c) for c in cmd], cwd=cwd, input=stdin, capture_output=True, check=False, timeout=240
    )


@pytest.fixture(scope="module")
def distributions(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, Path]:
    dist = tmp_path_factory.mktemp("distributions")
    built = _run(sys.executable, "-m", "build", "--outdir", dist, ROOT)
    assert built.returncode == 0, built.stderr
    (wheel,) = dist.glob("viaheader-*.whl")
    (sdist,) = dist.glob("viaheader-*.tar.gz")
    return wheel, sdist


def test_installed_wheel_end_to_end(tmp_path: Path, distributions: tuple[Path, Path]) -> None:
    wheel, sdist = distributions
    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
        metadata = BytesParser().parsebytes(archive.read("viaheader-1.0.0.dist-info/METADATA"))
        assert metadata["Version"] == "1.0.0"
        assert metadata["Requires-Python"] == ">=3.10"
        assert "Development Status :: 5 - Production/Stable" in metadata.get_all("Classifier", [])
        assert all("extra == 'dev'" in r for r in metadata.get_all("Requires-Dist", []))
        assert "Source, https://github.com/JaviLianes8/viaheader" in metadata.get_all(
            "Project-URL", []
        )
    assert "viaheader/py.typed" in names
    assert "viaheader/__main__.py" in names
    assert "viaheader-1.0.0.dist-info/licenses/LICENSE" in names
    assert not any(name.startswith(("tests/", "scripts/", "scratchpad/")) for name in names)
    with tarfile.open(sdist) as archive:
        listing = "\n".join(archive.getnames())
    assert "IMPROVEMENTS-round" not in listing
    assert "CERT-" not in listing
    assert "scratchpad" not in listing
    assert "/LICENSE" in listing and "/GUIDE.md" in listing
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
        # Hand-written folded comment: Latin-1 whitespace remains comment content.
        folded = _run(*command, "--strict", cwd=work, stdin=b"Via: 1.1 edge (\r\n \xa0)\r\n\r\n")
        assert folded.returncode == 0, folded.stderr
        assert folded.stderr == b""
        assert json.loads(folded.stdout)[0]["comment"] == " \u00a0"
    rejected = _run(bindir / "viaheader", "--strict", "1.1 a (", cwd=work)
    assert rejected.returncode == 1
    assert b"unterminated comment" in rejected.stderr
    with subprocess.Popen(
        [str(python), "-I", "-m", "viaheader"],
        cwd=work,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ) as process:
        assert process.stdout is not None and process.stdin is not None
        assert process.stderr is not None
        process.stdout.close()
        process.stdin.write(block)
        process.stdin.close()
        error = process.stderr.read()
        assert process.wait(timeout=30) == 1, error
        assert not error


@pytest.mark.skipif(os.environ.get("VIAHEADER_E2E_PYPI") != "1", reason="opt-in PyPI upgrade")
def test_pypi_upgrade_and_pickle_compatibility(
    tmp_path: Path, distributions: tuple[Path, Path]
) -> None:
    wheel, _ = distributions
    venv.create(tmp_path / "env", with_pip=True)
    bindir = tmp_path / "env" / ("Scripts" if sys.platform == "win32" else "bin")
    python = bindir / "python"
    installed = _run(python, "-m", "pip", "install", "--no-deps", "viaheader==0.2.0")
    assert installed.returncode == 0, installed.stderr
    baseline = _run(python, "-I", "-c", PROGRAM, cwd=tmp_path)
    assert baseline.returncode == 0, baseline.stderr
    snapshot = Path(__file__).with_name("upgrade_snapshot.py")
    old = _run(python, "-I", snapshot, cwd=tmp_path)
    assert old.returncode == 0, old.stderr
    old_pickle = _run(
        python,
        "-I",
        "-c",
        "import pickle,sys; from viaheader import Hop,ViaError; "
        "sys.stdout.buffer.write(pickle.dumps((Hop('edge','2'),ViaError('bad',line=1,position=2))))",
        cwd=tmp_path,
    )
    assert old_pickle.returncode == 0, old_pickle.stderr
    hop, error = pickle.loads(old_pickle.stdout)
    assert hop == Hop("edge", "2") and isinstance(error, ViaError)
    assert (error.line, error.position) == (1, 2)
    reverse = _run(
        python,
        "-I",
        "-c",
        "import pickle,sys; from viaheader import Hop,ViaError; "
        "h,e=pickle.loads(sys.stdin.buffer.read()); assert h==Hop('edge','2'); "
        "assert isinstance(e,ViaError) and (e.line,e.position)==(1,2)",
        cwd=tmp_path,
        stdin=pickle.dumps((Hop("edge", "2"), ViaError("bad", line=1, position=2))),
    )
    assert reverse.returncode == 0, reverse.stderr
    upgraded = _run(python, "-m", "pip", "install", "--no-deps", "--upgrade", wheel)
    assert upgraded.returncode == 0, upgraded.stderr
    new = _run(python, "-I", snapshot, cwd=tmp_path)
    assert new.returncode == 0, new.stderr
    assert json.loads(old.stdout) == json.loads(new.stdout)
    result = _run(python, "-I", "-c", PROGRAM, cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    cli = _run(bindir / "viaheader", "--strict", "1.1 edge", cwd=tmp_path)
    assert cli.returncode == 0 and json.loads(cli.stdout)[0]["host"] == "edge"
