"""What a proxy does with Via: append its own entry, and look for itself to stop a loop."""

from __future__ import annotations

import ipaddress
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
    swallow or forge the entry added here. Received entries in the RFC 7230 IP-literal
    form are kept; map them in ``pseudonyms`` to forward pure RFC 9110. ``pseudonyms``
    maps received-by hosts, without a port and matched without regard to case, to the
    pseudonym that replaces the whole received-by, as RFC 9110 asks of a proxy that
    hides hosts behind a firewall. ``drop_comments`` removes received
    comments. ``hop`` itself must be valid RFC 9110, or ``ViaError`` is raised.

    >>> from viaheader import Hop, append
    >>> append("1.0 internal:80 (cache)", Hop("edge", "1.1"),
    ...        pseudonyms={"INTERNAL": "fw"}, drop_comments=True)
    '1.0 fw, 1.1 edge'
    """
    own = render(hop, legacy=False)
    renames = _renames(pseudonyms)
    entries: list[str] = []
    for received in parse(existing):
        pseudonym = renames.get(_host_key(received.host))
        if pseudonym is not None:
            received = replace(received, received_by=pseudonym)
        if drop_comments:
            received = replace(received, comment=None)
        entries.append(render(received, legacy=True))
    entries.append(own)
    return ", ".join(entries)


def _renames(pseudonyms: Mapping[str, str] | None) -> dict[str, str]:
    if pseudonyms is not None and not isinstance(pseudonyms, Mapping):
        raise TypeError("pseudonyms must be a mapping of str hosts to str pseudonyms")
    renames: dict[str, str] = {}
    for host, pseudonym in (pseudonyms or {}).items():
        if not isinstance(host, str) or not isinstance(pseudonym, str):
            raise TypeError("pseudonyms maps str hosts to str pseudonyms")
        host, pseudonym = str.__str__(host), str.__str__(pseudonym)
        if not is_token(pseudonym):
            raise ViaError("pseudonym is not a token")
        if not valid_received_by(host, legacy=True) or Hop(host, "1.1").host != host:
            raise ViaError("pseudonyms key is not a host without a port")
        renames[_host_key(host)] = pseudonym
    return renames


def has_loop(value: str | Iterable[str] | None, name: str, *names: str) -> bool:
    """Whether a received-by in ``value`` is one of this proxy's own names.

    A name is a host or pseudonym, matched without regard to case, with an optional
    ``:port``: without a port it matches the host on any port, with one it matches only
    that port. IPv6 literals match in any of their spellings. The value is parsed
    leniently, so the entries proxies appended are found whatever a client wrote in
    front of them.

    >>> from viaheader import has_loop
    >>> has_loop("1.0 client (, 1.1 Edge:443", "edge")
    True
    >>> has_loop("1.1 edge:80", "edge:443")
    False
    """
    wanted = [_split_name(each) for each in (name, *names)]
    any_port = {host for host, port in wanted if port is None}
    exact = set(wanted)
    for hop in parse(value):
        host = _host_key(hop.host)
        if host in any_port or (host, hop.port) in exact:
            return True
    return False


def _split_name(name: str) -> tuple[str, int | None]:
    if not isinstance(name, str):
        raise TypeError("a proxy name must be a str")
    name = str.__str__(name)
    if not valid_received_by(name, legacy=True):
        raise ViaError("proxy name is not a host or pseudonym with an optional port")
    probe = Hop(name, "1.1")
    if probe.port is None and len(name) > len(probe.host) + 1:
        raise ViaError("proxy name has a port above 65535")
    return _host_key(probe.host), probe.port


def _host_key(host: str) -> str:
    """A host as compared: case folded, an IPv6 literal in its compressed form."""
    if host.startswith("["):
        return f"[{ipaddress.IPv6Address(host[1:-1]).compressed}]"
    return host.lower()
