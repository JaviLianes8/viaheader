"""Parse, build and append the HTTP Via header per RFC 9110, typed and zero-dependency."""

from __future__ import annotations

from ._build import build
from ._errors import ViaError
from ._forward import append, has_loop
from ._model import Hop
from ._parse import parse

__version__ = "0.2.0"

__all__ = ["Hop", "ViaError", "append", "build", "has_loop", "parse"]
