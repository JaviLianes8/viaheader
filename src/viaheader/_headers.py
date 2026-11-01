"""Read successive header blocks without consuming an ignored body."""

from __future__ import annotations

import io
from typing import BinaryIO, TextIO


def via_lines(block: str) -> list[str]:
    """The Via values of the last response, with folded lines joined."""
    return read_headers(io.StringIO(block))


def _text(raw: str | bytes) -> str:
    # Header bytes map one to one to code points, independent of the terminal encoding.
    return raw.decode("latin-1") if isinstance(raw, bytes) else raw


def _next_response(stream: TextIO | BinaryIO) -> bool:
    prefix = ""
    while prefix != "HTTP/":
        char = _text(stream.read(1))
        if not char:
            return False
        prefix += char
        if prefix in ("\n", "\r\n"):
            prefix = ""
        elif prefix != "\r" and not "HTTP/".startswith(prefix):
            return False
    return True


def read_headers(stream: TextIO | BinaryIO) -> list[str]:
    """Read LF-delimited headers, stopping at EOF or the first body prefix."""
    lines: list[list[str]] = []
    state = "start"
    in_via = False
    while True:
        if state == "between":
            if not _next_response(stream):
                break
            stream.readline()
            lines, state = [], "header"
            continue
        raw = _text(stream.readline())
        if not raw:
            break
        raw = raw.removesuffix("\n").removesuffix("\r")
        if state == "start":
            if raw == "":
                continue
            state = "header"
        if raw == "":
            state, in_via = "between", False
        elif raw[:1] in (" ", "\t"):
            if in_via:
                lines[-1].append(raw.strip(" \t"))
        else:
            name, colon, value = raw.partition(":")
            in_via = bool(colon) and name.lower() == "via"
            if in_via:
                lines.append([value.strip(" \t")])
    return [" ".join(parts) for parts in lines]
