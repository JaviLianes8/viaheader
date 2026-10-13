"""Scan one Via field line into hops, strictly or with a safe recovery."""

from __future__ import annotations

import ipaddress

from ._chars import DIGITS, TCHAR, WHITESPACE, first_invalid
from ._comment import Broken as _Broken
from ._comment import Comments
from ._errors import ViaError
from ._model import Hop

# RFC 9110 section 5.5: a recipient may replace CR, LF and NUL with SP instead of rejecting.
_BLANKED = str.maketrans({"\r": " ", "\n": " ", "\0": " "})
_IP_LITERAL = frozenset("0123456789abcdefABCDEF:.")


def scan_line(line: str, *, strict: bool, index: int) -> list[Hop]:
    """Return the hops of one field line.

    Lenient mode drops an invalid entry and resumes at the first comma after the point
    where it broke; for a comment that never closes, that point is its opening
    parenthesis. Text a client writes therefore cannot hide entries appended after it.
    """
    if strict:
        bad = first_invalid(line)
        if bad != -1:
            raise ViaError(f"invalid character {line[bad]!r}", line=index, position=bad)
    else:
        line = line.translate(_BLANKED)
    comments = Comments(line)
    hops: list[Hop] = []
    pos = 0
    while True:
        pos = _skip_whitespace(line, pos)
        if pos >= len(line):
            return hops
        if line[pos] == ",":
            pos += 1
            continue
        try:
            hop, pos = _entry(comments, pos, strict)
        except _Broken as broken:
            if strict:
                raise ViaError(broken.reason, line=index, position=broken.at) from None
            comma = line.find(",", broken.at)
            if comma == -1:
                return hops
            pos = comma
            continue
        hops.append(hop)


def _entry(comments: Comments, pos: int, strict: bool) -> tuple[Hop, int]:
    line = comments.line
    name, pos = _token(line, pos, "a protocol version")
    protocol, version = "HTTP", name
    if pos < len(line) and line[pos] == "/":
        # Hop stores any spelling of HTTP as "HTTP".
        protocol = name
        version, pos = _token(line, pos + 1, "a protocol version after '/'")
    gap = _skip_whitespace(line, pos)
    if gap == pos:
        raise _Broken(pos, "expected whitespace after the received-protocol")
    received_by, pos = _received_by(line, gap, strict)
    gap = _skip_whitespace(line, pos)
    comment = None
    if gap < len(line) and line[gap] == "(":
        if strict and gap == pos:
            raise _Broken(pos, "expected whitespace before the comment")
        comment, pos = comments.read(gap)
        gap = _skip_whitespace(line, pos)
    if gap < len(line) and line[gap] != ",":
        raise _Broken(gap, f"unexpected {line[gap]!r} after the entry")
    return Hop(received_by, version, protocol, comment), gap


def _token(line: str, pos: int, what: str) -> tuple[str, int]:
    end = pos
    while end < len(line) and line[end] in TCHAR:
        end += 1
    if end == pos:
        raise _Broken(pos, f"expected {what}")
    return line[pos:end], end


def _received_by(line: str, pos: int, strict: bool) -> tuple[str, int]:
    start = pos
    if not strict and pos < len(line) and line[pos] == "[":
        # RFC 7230 allowed an IP literal here; RFC 9110 dropped it, so only lenient mode reads it.
        end = pos + 1
        while end < len(line) and line[end] in _IP_LITERAL:
            end += 1
        if end >= len(line) or line[end] != "]" or not _is_ipv6(line[pos + 1 : end]):
            raise _Broken(pos, "invalid IP literal")
        pos = end + 1
    else:
        _, pos = _token(line, pos, "a received-by host or pseudonym")
    if pos < len(line) and line[pos] == ":":
        pos += 1
        while pos < len(line) and line[pos] in DIGITS:
            pos += 1
    return line[start:pos], pos


def _is_ipv6(text: str) -> bool:
    try:
        ipaddress.IPv6Address(text)
    except ValueError:
        return False
    return True


def _skip_whitespace(line: str, pos: int) -> int:
    while pos < len(line) and line[pos] in WHITESPACE:
        pos += 1
    return pos
