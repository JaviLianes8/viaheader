# viaheader improvement round

Progress:
- [x] Brainstorm ranked improvements (this file)
- [x] Pin the ground truth: RFC 9110, RFC 9112, RFC 3986, MDN Via
- [x] Grammar-aware scanner: comments with nesting and quoted-pairs, per-line lists, safe resync
- [x] Strict mode with `ViaError`: RFC 9110 section 7.6.3 grammar, field value characters
- [x] Typed hops: decoded comments, `host` and `port`, HTTP name normalised
- [x] Safe builder: token and port checks, comment escaping, no header injection
- [x] Forwarding helpers: `append` with pseudonyms and comment removal, `has_loop`
- [x] Command line: `python -m viaheader` reads values or a header block, prints JSON
- [x] Contracts: RFC and MDN examples from the pinned files, round-trip fuzz, README examples, installed wheel
- [x] Docs and packaging: README, CHANGELOG, docstrings, metadata, sdist contents
- [x] Gates: ruff format, ruff check, mypy --strict, pytest
- [x] Mutation run: removing guarded logic makes the suite fail
- [x] Independent review findings fixed with regression tests
- [x] Pull request opened (#2), guard clean

## Starting point

`0.1.0` gives `Hop`, `parse` and `build`. Compared with the sources below:

- A comment that is never closed swallows every hop after it. A client that sends
  `Via: 1.0 x (` makes the entry its proxy appends (`, 1.1 edge`) disappear, so a proxy
  that looks for its own name to stop a request loop never finds it.
- Text after a comment or after the received-by is ignored instead of making the entry
  invalid (`1.1 a b c` reads as `1.1 a`).
- Comments come back with their quoted-pairs still escaped, so `(a \) b)` reads as
  `a \) b`.
- `build` writes anything: a received-by holding CR LF injects a header, and a comment
  holding `), 1.1 forged (` forges a hop.
- There is no strict mode, so a caller cannot tell a valid value from garbage, and no
  way to pass several field lines without joining them first.
- Nothing helps with the two jobs the field exists for: appending this proxy's own entry
  safely and detecting a loop.

## Sources (fetched 2026-10-13)

- RFC 9110, https://www.rfc-editor.org/rfc/rfc9110.txt (sha256 21c1cdce...7232a): Via
  grammar and rules (7.6.3), received-protocol names (7.8), lists and the recipient rule
  for empty elements (5.6.1), token (5.6.2), OWS and RWS (5.6.3), quoted-pair (5.6.4),
  comment and ctext (5.6.5), field values and CR, LF, NUL (5.5), combining field lines
  (5.3), the received-by change from RFC 7230 (B.2), disclosure of hosts (17.12). The
  errata page https://www.rfc-editor.org/errata/rfc9110 lists nothing for Via.
- RFC 9112, https://www.rfc-editor.org/rfc/rfc9112.txt: OWS around a field line value
  (5.1) and obsolete line folding replaced by SP (5.2).
- RFC 3986 section 3.2.3, https://www.rfc-editor.org/rfc/rfc3986.txt: `port = *DIGIT`.
- MDN, Via, mdn/content commit ad5b5e31f81795d692e66dadb7818ba8b220ad15: three example
  lines, among them `HTTP/1.1 GWA` with the protocol name written out.
- None of these files is committed. `tests/upstream/MANIFEST.json` records URL,
  revision, size, sha256 and licence; `scripts/fetch_upstream.py` fetches them into the
  ignored `tests/upstream/` folder and their tests skip while they are absent. Vendor
  values such as `1.1 varnish (Varnish/7.4)` in the tests are hand-written and labelled.

## Ranked improvements

1. **Safe resync.** After an invalid entry, scanning resumes at the first comma after the
   point where the entry broke, and for a comment that never closes that point is its
   opening parenthesis. A well-formed suffix appended by a proxy therefore always parses
   to the same hops, whatever the client wrote before it. Each field line is its own
   list. Proven by a seeded fuzz test over random prefixes.
2. **Strict mode.** `parse(value, strict=True)` raises `ViaError` (a `ValueError` with
   the line and offset) for anything outside the 7.6.3 grammar, CTL characters and code
   points above U+00FF. Empty list elements stay accepted, as 5.6.1.2 requires.
3. **Typed hops.** Comments are decoded (quoted-pairs resolved, nesting kept), `host` and
   `port` split the received-by, `HTTP` is normalised whatever its case.
4. **Safe builder.** `build` checks every token and port, refuses CTLs, escapes
   backslashes and unbalanced parentheses in comments, so `parse(build(hops)) == hops`.
5. **Forwarding helpers.** `append(existing, hop)` rebuilds the received value from
   its readable hops and adds the new one, with options to replace hosts by
   pseudonyms (7.6.3, 17.12) and to drop comments. `has_loop(value, name)` checks the
   received-by hosts, case-insensitive, with or without a port.
6. **Command line.** `python -m viaheader` prints the hops of the values given, or of the
   Via lines in a header block on stdin (the output of `curl -sI`), as JSON.
7. **Contracts.** RFC and MDN examples read from the pinned files; character classes
   derived from the fetched ABNF; README examples run; the installed wheel is driven
   from an empty folder.
8. **Docs and packaging.** README with executed examples and an API table, CHANGELOG,
   keywords and classifiers, sdist without planning notes or third-party files.

## Out of scope

- Collapsing entries with the same received-protocol (7.6.3 allows it under conditions a
  library cannot check: same organisation, pseudonyms already applied).
- Default ports per protocol: the RFC only says a recipient MAY assume one.
- Framework middleware: every framework exposes headers as strings, which is the input.

## Verification

- Gates on CPython 3.13.2 (this PC) and 3.14.2 (a second Windows machine), each in a
  fresh clone of the pushed branch with its own venv:
  `ruff format --check .`, `ruff check .`, `mypy --strict src` (and `src tests`) and
  `pytest`. The fetch script downloaded the four reference files and checked them
  against the manifest. With `VIAHEADER_E2E=1` the installed-wheel test builds the wheel
  and sdist, checks their contents (no planning notes, no fetched files, the manifest and
  fetch script present), installs the wheel in a fresh venv and drives the API, the
  `python -m viaheader` module and the `viaheader` command from an empty folder.
- Guarded logic was changed one piece at a time, with no bytecode written, caches purged
  before every run, a two-minute timeout per mutant and a green baseline before and
  after. First run (58 mutations): nine alive. Four were equivalent (a strict
  pre-check that only shaped the message, a ctext set the earlier branches already
  narrowed, a resume offset kept apart from the error offset): the code was simplified
  so lenient parsing resumes at the offset where the entry broke, as documented. Five
  were missing tests (a bad character inside a comment, the strict message for a stray
  control, a port after junk in a hand-built bracketed value, a colon-less `via` line,
  tab folding), now added. Second run (56 mutations): none alive.
- After the review fixes the run was redone with 77 mutations (42 of the first run that
  still apply, 35 on the new code): two alive, both equivalent (a separate message for
  a bad character after a backslash, which strict mode never reaches because its
  character check reports first); that split was removed.
- The review regression tests were run against the code before the fixes: 31 of them
  fail there, and the linear-time tests do not finish within 90 seconds.

## Review fixes

An independent review attacked the branch; each finding below is fixed with a test that
fails on the code before the fix:

- Quadratic time: every unclosed comment was scanned to the end of the line, so a value
  made of `1 a (,` repeated took 47 s at 72 KB, through `parse`, `has_loop` and
  `append`. Each line is now indexed once (where every parenthesis closes, where the
  next invalid character sits), and 256 KB of each hostile pattern parse in well under a
  second.
- A port of thousands of digits made `Hop.port` hit the integer conversion limit and
  crash `has_loop` and the command line. `port` is now `None` above 65535, checked by
  length before converting, and a proxy name with such a port raises `ViaError`.
- The command line decoded stdin with the locale; it now reads bytes as latin-1.
- The command line split lines on vertical tab, form feed, U+0085 and others, so
  another field could smuggle a `Via` line; only LF ends a line now. It also read past
  the blank line into the body; now it stops there, and with several responses
  (`curl -sIL`) uses the last.
- `parse(build(hops)) == hops` failed for `protocol="http"` or `""`; `Hop` now stores any
  spelling of HTTP as `HTTP`, and the fuzz test generates those spellings.
- A `pseudonyms` key with a port never matched, leaking the host it should hide. Keys
  must be hosts without a port; IPv6 keys and `has_loop` names match any spelling.
- Docs: `append` keeps received RFC 7230 IPv6 entries (map them to pseudonyms for pure
  RFC 9110), passes comments with their commas (use `drop_comments=True` before a naive
  parser), comments above U+00FF are refused, and this file no longer claims `append`
  keeps a value verbatim. Errors from the command line go to an injectable stream, and
  a terminal on stdin gives a usage error instead of waiting.
- Not changed: lower-case `http/1.1` stays accepted in strict mode (RFC 9110 section 7.8
  compares protocol names case-insensitively); trailing dots in names are not folded;
  IPvFuture literals stay unread; the Python floor stays at 3.10 as on `main`.
