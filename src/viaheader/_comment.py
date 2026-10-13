"""Comments of one field line, indexed in a single pass so reading them stays linear."""

from __future__ import annotations

from ._chars import QUOTABLE


class Broken(Exception):
    """An invalid entry and the offset where it broke."""

    def __init__(self, at: int, reason: str) -> None:
        super().__init__(reason)
        self.at = at
        self.reason = reason


class Comments:
    """Where each "(" of a line closes and where the next invalid character sits.

    A comment opens only after whitespace or a received-by, never right after a
    backslash, so the escapes read from the start of the line are the escapes a scan
    from any opening parenthesis would read. Scanning from each opening instead lets a
    line of unclosed comments cost quadratic time.
    """

    def __init__(self, line: str) -> None:
        self.line = line
        self._close: dict[int, int] = {}
        self._escaped_bad: set[int] = set()
        bad = [False] * len(line)
        opened: list[int] = []
        pos = 0
        while pos < len(line):
            char = line[pos]
            if char == "\\":
                if pos + 1 < len(line) and line[pos + 1] not in QUOTABLE:
                    bad[pos + 1] = True
                    self._escaped_bad.add(pos + 1)
                pos += 2
                continue
            if char == "(":
                opened.append(pos)
            elif char == ")":
                if opened:
                    self._close[opened.pop()] = pos
            elif char not in QUOTABLE:
                bad[pos] = True
            pos += 1
        self._next_bad = [len(line)] * (len(line) + 1)
        for index in range(len(line) - 1, -1, -1):
            self._next_bad[index] = index if bad[index] else self._next_bad[index + 1]

    def read(self, opening: int) -> tuple[str, int]:
        """The decoded text of the comment opening at ``opening`` and the offset after it.

        Nested comments stay in the text, quoted-pairs are resolved.
        """
        close = self._close.get(opening)
        limit = len(self.line) if close is None else close
        bad = self._next_bad[opening + 1]
        if bad < limit:
            if bad in self._escaped_bad:
                raise Broken(bad, "invalid character after a backslash")
            raise Broken(bad, f"invalid character {self.line[bad]!r} in a comment")
        if close is None:
            raise Broken(opening, "unterminated comment")
        text: list[str] = []
        pos = opening + 1
        while pos < close:
            if self.line[pos] == "\\":
                pos += 1
            text.append(self.line[pos])
            pos += 1
        return "".join(text), close + 1
