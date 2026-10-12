"""The data model for a single Via hop."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Hop:
    """One Via entry: an intermediary that received and forwarded the message."""

    received_by: str
    version: str
    protocol: str = "HTTP"
    comment: str | None = None
