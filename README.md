# viaheader

[![Lianes8 Certified](https://lianes8studio.com/certified/lianes8-certified-badge.svg)](https://lianes8studio.com/certified)

Parse, build and append the HTTP `Via` header per RFC 9110: strict or safely lenient,
typed, zero-dependency.

## Install

```
pip install viaheader
```

## Usage

### Read a Via header

```python
from viaheader import parse

hops = parse("1.0 fred, HTTP/1.1 p.example.net:8080 (Varnish/7.4)")
for hop in hops:
    print(hop.protocol, hop.version, hop.host, hop.port, hop.comment)
# HTTP 1.0 fred None None
# HTTP 1.1 p.example.net 8080 Varnish/7.4

# Several field lines are read in order, each as its own list; None means no header.
print(len(parse(["1.0 a", "1.1 b, 1.1 c"])), parse(None))
# 3 []
```

Each `Hop` carries `received_by` (a host or pseudonym with an optional `:port`, split
into `host` and `port`; `port` is `None` when absent or above 65535), the protocol
`version`, the `protocol` name (`HTTP` when the entry gives only a version, and any
spelling of `HTTP` is stored as `HTTP`) and the decoded `comment`, with quoted-pairs
resolved and nested parentheses kept, or `None`. Values are `str` holding the header
bytes decoded as latin-1, and parsing takes linear time whatever a client sends.

### Lenient by default, strict on request

```python
from viaheader import ViaError, parse

# A client opened a comment it never closed; the entry the proxy appended still reads.
print(parse("1.0 client (, 1.1 edge"))
# [Hop(received_by='edge', version='1.1', protocol='HTTP', comment=None)]

try:
    parse("1.0 client (, 1.1 edge", strict=True)
except ViaError as error:
    print(error, error.position)
# unterminated comment (line 0, offset 11) 11
```

The lenient parser skips an invalid entry and resumes at the first comma after the
point where it broke. For a comment that never closes, that point is its opening
parenthesis, so text written before an entry can never swallow or rewrite it. It also
replaces CR, LF and NUL with spaces (RFC 9110 section 5.5) and reads the bracketed IPv6
received-by that RFC 7230 allowed. `strict=True` raises `ViaError`, a `ValueError` with
the field `line` and the `position`, for anything outside the RFC 9110 grammar.

### Forward a request

```python
from viaheader import Hop, append, has_loop

received = "1.1 lb.internal:8080 (squid), 1.0 client ("
me = Hop("edge", "1.1", comment="viaheader")

print(has_loop(received, "edge"), has_loop(received + ", 1.1 Edge:443", "edge"))
# False True
print(append(received, me, pseudonyms={"lb.internal": "lb"}))
# 1.1 lb (squid), 1.1 edge (viaheader)
```

`append` writes the received hops back clean, in order, and adds yours at the end: an
entry that cannot be read is dropped instead of passed on, `pseudonyms` replaces hosts
behind a firewall (RFC 9110 sections 7.6.3 and 17.12) and `drop_comments=True` removes
received comments. `pseudonyms` keys are hosts without a port, matched without regard
to case. Entries received in the RFC 7230 bracketed IPv6 form are kept as they are, so
map them in `pseudonyms` when the next hop expects strict RFC 9110. Received comments
are passed on with their commas, which is valid but misleads a downstream parser that
splits on every comma; use `drop_comments=True` when the next hop might be one.

`has_loop` matches your names without regard to case, and IPv6 literals in any
spelling; a name without a port matches any port. A client can write your name into its
own `Via` too, so a match proves a loop only when the entry came from a proxy you trust.

### Build a header

```python
from viaheader import Hop, build, parse

value = build([Hop("gw", "1.0", protocol="FTP", comment="a ) b"), Hop("proxy", "1.1")])
print(value)
# FTP/1.0 gw (a \) b), 1.1 proxy
print(parse(value, strict=True)[0].comment)
# a ) b
```

`build` writes only valid RFC 9110: it raises `ViaError` for a protocol, version or
received-by that is not a token (with an optional port) and for a comment holding CR,
LF, another control or a character above U+00FF. It escapes backslashes and unpaired
parentheses in comments, so no header can be injected, no hop can be forged for an RFC
9110 parser, and `parse(build(hops)) == hops`.

### Command line

```
$ curl -sI https://example.com | python -m viaheader
$ python -m viaheader --strict "1.0 fred, 1.1 p.example.net"
```

Prints the hops as JSON. Without values it reads a header block from stdin as latin-1
and uses its `Via` lines; with several responses (`curl -sIL`) the last one counts, and
a body after the blank line is not read. With `--strict` an invalid value exits with
status 1 and the reason.
Unknown options exit 2 without echoing their values; a closed output pipe exits 1.

## API

| Name | What it does |
| --- | --- |
| `parse(value, *, strict=False)` | Hops of a value, a list of field lines, or `None` |
| `build(hops)` | One Via value, validated and escaped |
| `append(existing, hop, *, pseudonyms=None, drop_comments=False)` | The value to forward |
| `has_loop(value, name, *names)` | Whether one of your names is already in the chain |
| `Hop` | Frozen dataclass: `received_by`, `version`, `protocol`, `comment`, `host`, `port` |
| `ViaError` | `ValueError` raised for invalid values, with `line` and `position` |

## Why

`Via` is how proxies record the chain a message went through and how they stop request
loops, but its grammar has corners: an optional protocol name, comments that nest and
hold escaped parentheses and commas, a list that may span field lines. A splitter on
commas gets those wrong, and a parser that lets a client's unclosed comment run on hides
the very entry a loop check is looking for. `viaheader` reads it the way RFC 9110
defines it, writes it so nothing can be injected, and has no dependencies.

Use `str.split(",")` if you control the input and know it has no comments. Use
[`email.message.Message`](https://docs.python.org/3/library/email.message.html)
to work with a complete mail message: its `get_all("Via")` retrieves raw field lines.
Pass those lines to `viaheader` when you need structured hops, validation, safe
forwarding or loop checks. This library does not send HTTP requests or verify that a
proxy's claimed identity is trustworthy.

The [GUIDE](https://github.com/JaviLianes8/viaheader/blob/main/GUIDE.md) describes the
stable API, error rules and upgrade from 0.2.0. See the
[CHANGELOG](https://github.com/JaviLianes8/viaheader/blob/main/CHANGELOG.md) for releases.

## Development

Install `pip install -e ".[dev]"`, then run `scripts/check.ps1`.
`python scripts/fetch_upstream.py` downloads the four references pinned in
`tests/upstream/MANIFEST.json`; their tests skip when the files are absent.
Set `VIAHEADER_UPSTREAM` to keep downloads outside the checkout. Set `VIAHEADER_E2E=1`
to build and inspect both distributions and test the installed wheel and CLI;
`VIAHEADER_E2E_PYPI=1` also checks an in-place upgrade from PyPI 0.2.0.

## License

MIT. See [LICENSE](https://github.com/JaviLianes8/viaheader/blob/main/LICENSE).

## Links

- Website: https://lianes8studio.com
- GitHub: https://github.com/JaviLianes8
- LinkedIn: https://www.linkedin.com/in/jlianes/
