"""The data model for a single Via hop."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Hop:
    """One Via entry: an intermediary that received and forwarded the message.

    ``received_by`` is the host or pseudonym with an optional ``:port``. ``protocol`` is
    the protocol name, ``HTTP`` when the entry gives only a version. ``comment`` is the
    decoded comment text (quoted-pairs resolved, nested parentheses kept) or ``None``.
    """

    received_by: str
    version: str
    protocol: str = "HTTP"
    comment: str | None = None

    @property
    def host(self) -> str:
        """The received-by without its port."""
        if self.received_by.startswith("["):
            literal, bracket, _ = self.received_by.partition("]")
            return literal + bracket
        return self.received_by.partition(":")[0]

    @property
    def port(self) -> int | None:
        """The port of the received-by as a number, or ``None`` when it has none."""
        rest = self.received_by[len(self.host) :]
        digits = rest[1:] if rest.startswith(":") else ""
        return int(digits) if digits.isascii() and digits.isdigit() else None
