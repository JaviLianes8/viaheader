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
    """The values of the Via field lines in a header block, folded lines joined with SP."""
    lines: list[str] = []
    in_via = False
    for raw in block.splitlines():
        if raw[:1] in (" ", "\t"):
            if in_via:
                lines[-1] += " " + raw.strip(" \t")
            continue
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


def main(
    argv: Sequence[str] | None = None, stdin: TextIO | None = None, stdout: TextIO | None = None
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
    lines = args.values or via_lines((stdin if stdin is not None else sys.stdin).read())
    try:
        hops = parse(lines, strict=args.strict)
    except ViaError as error:
        print(f"viaheader: {error}", file=sys.stderr)
        return 1
    json.dump([_as_json(hop) for hop in hops], out, indent=2)
    out.write("\n")
    return 0
