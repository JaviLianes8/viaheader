"""Parse and build the HTTP Via header per RFC 9110, typed and zero-dependency."""

from __future__ import annotations

from ._build import build
from ._model import Hop
from ._parse import parse

__version__ = "0.1.0"

__all__ = ["Hop", "build", "parse"]
