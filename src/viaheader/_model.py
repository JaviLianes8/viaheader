"""The data model for a single Via hop."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Hop:
    """One Via entry: an intermediary that received and forwarded the message.

    ``received_by`` is the host or pseudonym with an optional ``:port``. ``protocol`` is
    the protocol name, ``HTTP`` when the entry gives only a version; any spelling of
    ``HTTP``, and the empty string, are stored as ``HTTP``. ``comment`` is the decoded
    comment text (quoted-pairs resolved, nested parentheses kept) or ``None``.
    """

    received_by: str
    version: str
    protocol: str = "HTTP"
    comment: str | None = None

    def __post_init__(self) -> None:
        # Protocol names compare case-insensitively (RFC 9110 section 7.8) and the name is
        # omitted for HTTP, so one spelling keeps equality and round trips exact.
        if isinstance(self.protocol, str) and self.protocol.upper() in ("HTTP", ""):
            object.__setattr__(self, "protocol", "HTTP")

    @property
    def host(self) -> str:
        """The received-by without its port."""
        if self.received_by.startswith("["):
            literal, bracket, _ = self.received_by.partition("]")
            return literal + bracket
        return self.received_by.partition(":")[0]

    @property
    def port(self) -> int | None:
        """The port of the received-by, or ``None`` when it has none or it exceeds 65535."""
        rest = self.received_by[len(self.host) :]
        digits = rest[1:] if rest.startswith(":") else ""
        if not (digits.isascii() and digits.isdigit()):
            return None
        # Checking the length first keeps int() away from client-sized digit strings.
        significant = digits.lstrip("0")
        if len(significant) > 5:
            return None
        number = int(significant or "0")
        return number if number <= 65535 else None
