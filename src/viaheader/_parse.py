"""Read Via field values into structured hops."""

from __future__ import annotations

from collections.abc import Iterable

from ._model import Hop
from ._scan import scan_line


def parse(value: str | Iterable[str] | None, *, strict: bool = False) -> list[Hop]:
    """Parse a Via field value, or several field lines given in order, into hops.

    ``None`` (a missing header) gives no hops.

    Each field line is read as its own list, so text in one line never reaches the next.
    By default an invalid entry is skipped and parsing resumes at a safe comma; with
    ``strict=True`` anything outside the RFC 9110 grammar raises ``ViaError``.
    """
    hops: list[Hop] = []
    for index, line in enumerate(field_lines(value)):
        hops.extend(scan_line(line, strict=strict, index=index))
    return hops


def field_lines(value: str | Iterable[str] | None) -> list[str]:
    """The field lines of a value given as one string, an iterable of strings or None."""
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, (bytes, bytearray, memoryview)):
        raise TypeError("Via values are str; decode the header bytes as latin-1 first")
    lines = list(value)
    for line in lines:
        if not isinstance(line, str):
            raise TypeError(f"each Via field line must be a str, not {type(line).__name__}")
    return lines
