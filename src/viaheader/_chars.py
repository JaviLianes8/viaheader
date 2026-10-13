"""Character classes from RFC 9110 sections 5.5, 5.6.2, 5.6.4 and 5.6.5."""

from __future__ import annotations

import string

TCHAR = frozenset("!#$%&'*+-.^_`|~" + string.digits + string.ascii_letters)
DIGITS = frozenset(string.digits)
WHITESPACE = frozenset(" \t")
# What may follow a backslash (quoted-pair): HTAB, SP, VCHAR and obs-text. ctext is the
# same set without the three characters a comment gives a meaning to.
QUOTABLE = frozenset(chr(code) for code in (0x09, *range(0x20, 0x7F), *range(0x80, 0x100)))


def is_token(text: str) -> bool:
    """A non-empty run of tchar."""
    return bool(text) and all(char in TCHAR for char in text)


def is_port(text: str) -> bool:
    """RFC 3986 port: any number of ASCII digits, including none."""
    return all(char in DIGITS for char in text)


def first_invalid(text: str) -> int:
    """Offset of the first character a field value cannot hold, or -1.

    Field values carry HTAB, SP, VCHAR and obs-text (U+0080 to U+00FF, the octets a
    latin-1 decoded header produces). CR, LF, NUL and the other controls are invalid.
    """
    for index, char in enumerate(text):
        if char not in QUOTABLE:
            return index
    return -1
