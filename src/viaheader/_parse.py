"""Read a Via header value into structured hops."""

from __future__ import annotations

from ._model import Hop


def parse(header: str) -> list[Hop]:
    """Parse a Via header value into hops, skipping entries that are not well formed."""
    hops: list[Hop] = []
    for element in _split_elements(header):
        hop = _parse_element(element)
        if hop is not None:
            hops.append(hop)
    return hops


def _split_elements(header: str) -> list[str]:
    """Split on commas that sit outside a comment, honouring escaped parentheses."""
    elements: list[str] = []
    buffer: list[str] = []
    depth = 0
    index = 0
    length = len(header)
    while index < length:
        char = header[index]
        if char == "\\" and depth > 0 and index + 1 < length:
            buffer.append(char)
            buffer.append(header[index + 1])
            index += 2
            continue
        if char == "(":
            depth += 1
        elif char == ")" and depth > 0:
            depth -= 1
        if char == "," and depth == 0:
            elements.append("".join(buffer))
            buffer = []
        else:
            buffer.append(char)
        index += 1
    elements.append("".join(buffer))
    return [element.strip() for element in elements if element.strip()]


def _parse_element(element: str) -> Hop | None:
    comment = None
    opening = element.find("(")
    if opening != -1:
        comment = _strip_parentheses(element[opening:])
        core = element[:opening].strip()
    else:
        core = element
    tokens = core.split()
    if len(tokens) < 2:
        return None
    protocol, version = _split_protocol(tokens[0])
    return Hop(received_by=tokens[1], version=version, protocol=protocol, comment=comment)


def _split_protocol(token: str) -> tuple[str, str]:
    """A received-protocol is an optional name and a version: HTTP when the name is absent."""
    if "/" in token:
        name, _, version = token.partition("/")
        return (name or "HTTP"), version
    return "HTTP", token


def _strip_parentheses(text: str) -> str | None:
    text = text.strip()
    if len(text) >= 2 and text[0] == "(" and text[-1] == ")":
        return text[1:-1]
    return None
