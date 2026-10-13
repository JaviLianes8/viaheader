"""What a proxy does with Via: append its own entry, and look for itself to stop a loop."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import replace

from ._build import render, valid_received_by
from ._chars import is_token
from ._errors import ViaError
from ._model import Hop
from ._parse import parse


def append(
    existing: str | Iterable[str] | None,
    hop: Hop,
    *,
    pseudonyms: Mapping[str, str] | None = None,
    drop_comments: bool = False,
) -> str:
    """Return the Via value to forward: the hops received, in order, then ``hop``.

    The received value is parsed leniently and written back clean, so an entry that
    cannot be read is dropped instead of being passed on, and nothing it holds can
    swallow or forge the entry added here. ``pseudonyms`` maps received-by hosts (case
    is ignored) to the pseudonym that replaces the whole received-by, as RFC 9110 asks
    of a proxy that hides hosts behind a firewall. ``drop_comments`` removes received
    comments. ``hop`` itself must be valid RFC 9110, or ``ViaError`` is raised.
    """
    own = render(hop, legacy=False)
    renames = _renames(pseudonyms)
    entries: list[str] = []
    for received in parse(existing):
        pseudonym = renames.get(received.host.lower())
        if pseudonym is not None:
            received = replace(received, received_by=pseudonym)
        if drop_comments:
            received = replace(received, comment=None)
        entries.append(render(received, legacy=True))
    entries.append(own)
    return ", ".join(entries)


def _renames(pseudonyms: Mapping[str, str] | None) -> dict[str, str]:
    renames: dict[str, str] = {}
    for host, pseudonym in (pseudonyms or {}).items():
        if not isinstance(host, str) or not isinstance(pseudonym, str):
            raise TypeError("pseudonyms maps str hosts to str pseudonyms")
        if not is_token(pseudonym):
            raise ViaError(f"pseudonym {pseudonym!r} is not a token")
        renames[host.lower()] = pseudonym
    return renames


def has_loop(value: str | Iterable[str] | None, name: str, *names: str) -> bool:
    """Whether a received-by in ``value`` is one of this proxy's own names.

    A name is a host or pseudonym, matched without regard to case, with an optional
    ``:port``: without a port it matches the host on any port, with one it matches only
    that port. The value is parsed leniently, so the entries proxies appended are found
    whatever a client wrote in front of them.
    """
    wanted = [_split_name(each) for each in (name, *names)]
    for hop in parse(value):
        host = hop.host.lower()
        for wanted_host, wanted_port in wanted:
            if host == wanted_host and (wanted_port is None or hop.port == wanted_port):
                return True
    return False


def _split_name(name: str) -> tuple[str, int | None]:
    if not isinstance(name, str):
        raise TypeError(f"a proxy name must be a str, not {type(name).__name__}")
    if not valid_received_by(name, legacy=True):
        raise ViaError(f"proxy name {name!r} is not a host or pseudonym with an optional port")
    probe = Hop(name, "1.1")
    return probe.host.lower(), probe.port
