"""Serialise hops back into a Via field value, refusing anything that is not RFC 9110."""

from __future__ import annotations

import ipaddress
from collections.abc import Iterable

from ._chars import QUOTABLE, is_port, is_token
from ._errors import ViaError
from ._model import Hop


def build(hops: Iterable[Hop]) -> str:
    """Render hops into one Via field value, omitting the HTTP protocol name.

    Raises ``ViaError`` for a protocol, version or received-by that is not valid RFC 9110
    syntax and for a comment holding characters a field value cannot carry. Comments are
    escaped as needed, so ``parse(build(hops)) == hops``.
    """
    return ", ".join(render(hop, legacy=False) for hop in hops)


def render(hop: Hop, *, legacy: bool) -> str:
    """One entry; ``legacy`` also accepts the bracketed IPv6 received-by of RFC 7230."""
    if not isinstance(hop, Hop):
        raise TypeError(f"expected a Hop, not {type(hop).__name__}")
    for field in ("received_by", "version", "protocol"):
        if not isinstance(getattr(hop, field), str):
            raise TypeError(f"Hop.{field} must be a str")
    if not is_token(hop.version):
        raise ViaError(f"protocol version {hop.version!r} is not a token")
    if hop.protocol == "" or hop.protocol.upper() == "HTTP":
        parts = [hop.version]
    elif is_token(hop.protocol):
        parts = [f"{hop.protocol}/{hop.version}"]
    else:
        raise ViaError(f"protocol name {hop.protocol!r} is not a token")
    if not valid_received_by(hop.received_by, legacy=legacy):
        raise ViaError(f"received-by {hop.received_by!r} is not a token with an optional port")
    parts.append(hop.received_by)
    if hop.comment is not None:
        parts.append(escape_comment(hop.comment))
    return " ".join(parts)


def valid_received_by(text: str, *, legacy: bool) -> bool:
    """RFC 9110 received-by; ``legacy`` adds the RFC 7230 bracketed IPv6 form."""
    if legacy and text.startswith("[") and "]" in text:
        literal, _, rest = text[1:].partition("]")
        try:
            ipaddress.IPv6Address(literal)
        except ValueError:
            return False
        return (
            literal.isascii()
            and "%" not in literal
            and (not rest or (rest[0] == ":" and is_port(rest[1:])))
        )
    host, colon, port = text.partition(":")
    return is_token(host) and (not colon or is_port(port))


def escape_comment(text: str) -> str:
    """Wrap text in parentheses, escaping backslashes and parentheses that do not pair up."""
    if not isinstance(text, str):
        raise TypeError("Hop.comment must be a str or None")
    unmatched: set[int] = set()
    opened: list[int] = []
    for index, char in enumerate(text):
        if char not in QUOTABLE:
            raise ViaError(f"comment holds {char!r}, which a field value cannot carry")
        if char == "(":
            opened.append(index)
        elif char == ")":
            if opened:
                opened.pop()
            else:
                unmatched.add(index)
    unmatched.update(opened)
    out = [
        "\\" + char if char == "\\" or index in unmatched else char
        for index, char in enumerate(text)
    ]
    return "(" + "".join(out) + ")"
