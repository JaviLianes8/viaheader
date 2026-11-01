"""Command line: print the hops of Via values, given as arguments or in a header block."""

from __future__ import annotations

import argparse
import errno
import io
import json
import sys
from collections.abc import Sequence
from typing import NoReturn, TextIO

from ._errors import ViaError
from ._headers import read_headers
from ._headers import via_lines as via_lines
from ._model import Hop
from ._parse import parse


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        if message.startswith("unrecognized arguments:"):
            message = "unrecognized arguments"
        elif message.startswith("argument "):
            message = "option does not accept a value"
        super().error(message)


def _as_json(hop: Hop) -> dict[str, object]:
    return {
        "protocol": hop.protocol,
        "version": hop.version,
        "received_by": hop.received_by,
        "host": hop.host,
        "port": hop.port,
        "comment": hop.comment,
    }


def main(
    argv: Sequence[str] | None = None,
    stdin: TextIO | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    """Run the command line; returns the exit status (1 when strict parsing fails)."""
    parser = _Parser(
        prog="viaheader",
        description="Print the hops of HTTP Via values as JSON. Without VALUE arguments, "
        "read a header block (for example the output of curl -sI) and use its Via lines.",
    )
    parser.add_argument("values", nargs="*", metavar="VALUE", help="a Via field line value")
    parser.add_argument("--strict", action="store_true", help="reject values outside RFC 9110")
    args = parser.parse_args(argv)
    out = stdout if stdout is not None else sys.stdout
    err = stderr if stderr is not None else sys.stderr
    if args.values:
        lines = list(args.values)
    elif stdin is not None:
        lines = read_headers(stdin)
    elif sys.stdin.isatty():
        parser.error("give VALUE arguments or pipe a header block on stdin")
    else:
        lines = read_headers(sys.stdin.buffer)
    try:
        hops = parse(lines, strict=args.strict)
    except ViaError as error:
        print(f"viaheader: {error}", file=err)
        return 1
    try:
        json.dump([_as_json(hop) for hop in hops], out, indent=2)
        out.write("\n")
        out.flush()
    except OSError as error:
        # Windows reports a closed anonymous pipe as EINVAL rather than EPIPE.
        if not isinstance(error, BrokenPipeError) and not (
            sys.platform == "win32" and error.errno == errno.EINVAL
        ):
            raise
        # Prevent the interpreter's final flush from retrying a closed stdout pipe.
        if out is sys.stdout:
            sys.stdout = io.StringIO()
        return 1
    return 0
