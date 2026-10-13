"""The single exception type the library raises for values it cannot accept."""

from __future__ import annotations


class ViaError(ValueError):
    """A Via value or hop that breaks RFC 9110.

    ``line`` is the index of the field line and ``position`` the offset inside it where
    parsing failed; both are ``None`` for errors raised while building.
    """

    def __init__(self, message: str, *, line: int | None = None, position: int | None = None):
        if position is not None:
            message = f"{message} (line {line}, offset {position})"
        super().__init__(message)
        self.line = line
        self.position = position
