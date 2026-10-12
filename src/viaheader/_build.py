"""Serialise hops back into a Via header value."""

from __future__ import annotations

from collections.abc import Iterable

from ._model import Hop


def build(hops: Iterable[Hop]) -> str:
    """Render hops into a single Via header value, dropping the HTTP protocol name."""
    return ", ".join(_build_element(hop) for hop in hops)


def _build_element(hop: Hop) -> str:
    if not hop.protocol or hop.protocol == "HTTP":
        protocol = hop.version
    else:
        protocol = f"{hop.protocol}/{hop.version}"
    parts = [protocol, hop.received_by]
    if hop.comment is not None:
        parts.append(f"({hop.comment})")
    return " ".join(parts)
