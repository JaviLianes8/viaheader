# viaheader guide

## Stable API

Import all public names from `viaheader`. The public surface is `Hop`, `ViaError`,
`parse`, `build`, `append` and `has_loop`. `__version__` is the package version string.

String subclasses are accepted by their underlying text. Hop fields, field lines,
pseudonyms and proxy names are normalized to built-in strings before processing;
overridden string methods do not change validation or serialization.

`Hop(received_by, version, protocol="HTTP", comment=None)` is a frozen, hashable
dataclass. Construction stores the supplied fields without checking syntax;
`build` and `append` validate before writing. Fields must have their annotated types
when used. Empty or case-insensitive HTTP protocol names become `HTTP`; other
protocol spellings are preserved. `host` removes the optional port and keeps IPv6
brackets. `port` returns an integer from 0 to 65535, or `None` for an absent, empty,
malformed or larger port. Leading zeros have no numerical effect. Port syntax in
the header itself is any number of ASCII digits, even zero or more than 65535.

`parse(value, *, strict=False)` accepts a string, an iterable of strings or `None`.
It returns a new list in wire order. Each field line is independent. Decode bytes
as latin-1 before calling it. Empty values and empty list members yield no hops.
Strict parsing follows the recipient rules of
[RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html#section-7.6.3), including
ignoring empty comma-separated members. A comment needs preceding space or tab.
Before parsing syntax, strict mode rejects the first forbidden field character;
otherwise it reports the first syntax failure. Offsets count Python string
characters and start at zero; the field-line index also starts at zero.

Lenient parsing replaces CR, LF and NUL with spaces and permits bracketed IPv6
addresses (without a zone identifier) and comments adjacent to received-by.
This IPv6 extension supports the older
[RFC 7230 form](https://www.rfc-editor.org/rfc/rfc7230.html#section-5.7.1), not its
entire host grammar. Invalid entries are discarded; scanning resumes at the first
comma following the failure. An unclosed comment fails at its opening parenthesis.
Nested comments retain parentheses; quoted-pairs lose the backslash.

`build(hops)` consumes an iterable of hops and writes one RFC 9110 field value,
joined with comma-space. It omits HTTP, preserves other protocol names, writes
comments with exactly one separating space, escapes backslashes and unpaired
parentheses, and retains paired nested parentheses. Empty input yields `""`.
Every accepted sequence satisfies `parse(build(hops), strict=True) == list(hops)`
when the iterable is reusable. No CR, LF or NUL can be emitted.

`append(existing, hop, *, pseudonyms=None, drop_comments=False)` leniently parses
the received fields, renders the accepted entries, then appends the validated hop.
Pseudonym keys are hosts without ports, matched case-insensitively; bracketed IPv6
spellings are normalized for matching. Replacements are tokens, replace the whole
received-by including its port, and affect received hops only. If keys normalize
to the same host, the last entry wins. Every mapping entry is checked even if unused.
`drop_comments` removes only received comments, never the new hop's comment.
Received IPv6 entries remain in legacy form unless mapped to a pseudonym.

`has_loop(value, name, *names)` searches leniently parsed received-by names. A name
without a port, or with an empty port, matches that host at any port. A numerical
port matches only the same number; zero is a specific port. Matching ignores ASCII
host case and normalizes IPv6 spellings. All names are checked before parsing,
including names following an earlier match. It does not establish trust: clients
can supply Via values too. Compare only identities meaningful to your deployment.

```python
from viaheader import Hop, append, build, has_loop, parse

raw = ["1.0 client (", "HTTP/1.1 internal:80 (cache)"]
forwarded = append(raw, Hop("edge", "2"), pseudonyms={"INTERNAL": "fw"})
assert forwarded == "1.1 fw (cache), 2 edge"
assert has_loop(forwarded, "EDGE:443", "edge")
assert parse(build(parse(forwarded)), strict=True) == parse(forwarded)
```

## Errors and limits

| Operation | Error contract |
| --- | --- |
| Strict `parse` | `ViaError`, with `line` and `position` |
| Lenient `parse` | Malformed entries skipped; wrong types raise `TypeError` |
| `build`, `append`, `has_loop` | `ViaError` for invalid values; `TypeError` for wrong types |
| `Hop` | Stores values; no eager syntax validation |
| `ViaError(message, *, line=None, position=None)` | `ValueError` subclass; formats position when supplied |

Library validation errors do not echo rejected field values. Parsing errors can
identify one invalid character. Messages and error classes are separate contracts:
error wording can improve, but the documented error families and position meaning
are stable. A directly constructed `ViaError` preserves the caller's own message.
Errors raised by caller-supplied iterators or streams propagate to the caller.

Parsing uses linear time and memory in the input size; nested comments use no
Python recursion. Loop detection indexes names rather than scanning every name for
each hop. There is no global input-size limit: apply your HTTP server's field-size
limits before parsing untrusted requests. Huge numerical ports are length-checked
before integer conversion. Comments are limited to the HTTP byte repertoire, not
arbitrary Unicode.

## CLI

`python -m viaheader` and `viaheader` print a JSON list with `protocol`, `version`,
`received_by`, `host`, `port` and `comment`. Arguments are field values, in order.
Without arguments, stdin is a latin-1 header block: Via fields are matched without
case, continuations unfold with spaces, and the last HTTP response block wins.
Input is read incrementally. After a blank line, further blank lines are skipped;
at most five characters of the next nonblank prefix distinguish `HTTP/` from a body.
Once a body is identified, reading stops without waiting for body EOF or allocating
memory for the remaining body. Stream buffers may read ahead. A header-only stream
still needs EOF to rule out a further response; a body beginning with `HTTP/` is
interpreted as another response, so this is a header-block reader, not HTTP framing.
Only LF ends lines; one preceding CR is removed. Output is ASCII-safe JSON.

Exit codes: 0 for success (including an empty list), 1 for strict syntax failure or
a closed output pipe, 2 for command-line misuse. Strict errors go to stderr without
JSON output. Unknown options are not echoed. The CLI accepts `--` before values
beginning with a hyphen.

## Upgrade from 0.2.0

Install with `pip install --upgrade viaheader`. The public names, signatures,
defaults, parsed values and serialized headers are unchanged. Validation errors
now avoid echoing the rejected value, and CLI usage errors omit invalid arguments.
Non-mapping `pseudonyms` now raise `TypeError`, including falsy values.
String subclasses are processed as their underlying built-in strings. The CLI
stops on an identified body prefix instead of buffering all stdin through EOF.
Closed output pipes exit 1 quietly. `Hop` and `ViaError` now report `viaheader` as
their module; pickles work in both directions with 0.2.0. Code importing private
modules is outside the public contract. The
[CHANGELOG](https://github.com/JaviLianes8/viaheader/blob/main/CHANGELOG.md)
lists the complete changes.
