# viaheader

Parse and build the HTTP Via header per RFC 9110, typed and zero-dependency

## Install

```
pip install viaheader
```

## Usage

```python
from viaheader import Hop, build, parse

hops = parse("1.1 proxy1, 1.0 proxy2:8080 (edge cache)")
# [Hop(received_by='proxy1', version='1.1', protocol='HTTP', comment=None),
#  Hop(received_by='proxy2:8080', version='1.0', protocol='HTTP', comment='edge cache')]

for hop in hops:
    print(hop.received_by, hop.version)

header = build([
    Hop(received_by="proxy1", version="1.1"),
    Hop(received_by="gw", version="1.0", protocol="FTP", comment="note"),
])
# "1.1 proxy1, FTP/1.0 gw (note)"
```

Each hop carries its `received_by` (a host, an optional `:port`, or a pseudonym),
the protocol `version`, the `protocol` name (defaulting to `HTTP` when only a version
is given), and an optional `comment`. A comment keeps its inner text and may contain
commas and spaces; `build` wraps it back in parentheses and drops the `HTTP` name, as
RFC 9110 allows. Entries that are not well formed are skipped rather than raising.

## Why

RFC 9110 defines the `Via` header as a comma-separated list of intermediaries, each a
received-protocol, a received-by, and an optional comment, with commas inside comments
that must not split the list. The Python ecosystem has no small, typed, zero-dependency
codec for it: the broad HTTP libraries either predate RFC 9110 or pull in a whole
framework, and the Java and curl implementations have no Python peer. `viaheader` does
one thing, both directions, with full type hints and nothing to install alongside it.

## License

MIT. See [LICENSE](LICENSE).

## Links

- Website: https://lianes8studio.com
- GitHub: https://github.com/JaviLianes8
- LinkedIn: https://www.linkedin.com/in/jlianes/
