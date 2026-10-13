"""Command line: print the hops of Via values, given as arguments or in a header block."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from typing import TextIO

from ._errors import ViaError
from ._model import Hop
from ._parse import parse


def via_lines(block: str) -> list[str]:
    """The Via field values of the last header block in ``block``, folded lines joined.

    Lines end at LF (a CR before it is dropped), as in HTTP/1.1; other line breaks are
    data. A blank line ends a header block. A status line (``HTTP/``) after it starts
    the next response, as in the output of ``curl -sIL``; anything else is a body and
    is not read.
    """
    lines: list[str] = []
    state = "start"
    in_via = False
    for raw in block.split("\n"):
        raw = raw.removesuffix("\r")
        if state == "between":
            if raw == "":
                continue
            if not raw.startswith("HTTP/"):
                break
            lines, state = [], "header"
            continue
        if state == "start":
            if raw == "":
                continue
            state = "header"
        if raw == "":
            state, in_via = "between", False
        elif raw[:1] in (" ", "\t"):
            if in_via:
                lines[-1] += " " + raw.strip(" \t")
        else:
            name, colon, value = raw.partition(":")
            in_via = bool(colon) and name.lower() == "via"
            if in_via:
                lines.append(value.strip(" \t"))
    return lines


def _as_json(hop: Hop) -> dict[str, object]:
    return {
        "protocol": hop.protocol,
        "version": hop.version,
        "received_by": hop.received_by,
        "host": hop.host,
        "port": hop.port,
        "comment": hop.comment,
    }


def _read_stdin() -> str:
    # Header bytes map to code points one to one in latin-1 (obs-text stays U+0080-U+00FF).
    return sys.stdin.buffer.read().decode("latin-1")


def main(
    argv: Sequence[str] | None = None,
    stdin: TextIO | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    """Run the command line; returns the exit status (1 when strict parsing fails)."""
    parser = argparse.ArgumentParser(
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
        lines = via_lines(stdin.read())
    elif sys.stdin.isatty():
        parser.error("give VALUE arguments or pipe a header block on stdin")
    else:
        lines = via_lines(_read_stdin())
    try:
        hops = parse(lines, strict=args.strict)
    except ViaError as error:
        print(f"viaheader: {error}", file=err)
        return 1
    json.dump([_as_json(hop) for hop in hops], out, indent=2)
    out.write("\n")
    return 0
