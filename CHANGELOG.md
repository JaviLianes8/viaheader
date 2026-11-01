# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-11-01

### Stable

- The six public names `Hop`, `ViaError`, `parse`, `build`, `append` and `has_loop`,
  with their existing signatures, defaults and error families from 0.2.0.
- RFC 9110 strict parsing, lenient recovery, immutable hops, comment escaping,
  pseudonym replacement, loop detection and the JSON command line.
- Python 3.10 through 3.14, type information and no runtime dependencies.

### Changed

- Invalid protocol, version, received-by, pseudonym and proxy-name errors no longer
  echo the rejected input. Wrong Hop/proxy-name type errors omit the type name;
  a field-line type name is limited to 40 characters. Error classes are unchanged.
- `append` rejects non-mapping `pseudonyms` with `TypeError`; 0.2.0 silently ignored
  falsy non-mappings and raised `AttributeError` for other non-mappings.
- `Hop` and `ViaError` identify their defining module as `viaheader`. Old pickles
  remain readable, and new pickles can still be read by 0.2.0.
- The incidental `annotations` module attribute is removed; `__all__` is unchanged.
- The CLI omits unknown arguments and unexpected option values from usage errors
  and exits 1 quietly when
  its output pipe closes, including when the failure occurs during flushing.
- Loop detection indexes the requested names, and CLI line unfolding joins fragments
  once, avoiding quadratic work with many names or continuation lines.

### Added

- Runnable public docstrings and a guide covering errors and upgrade compatibility.
- Contract tests, seeded properties, live specification checks and wheel upgrade tests.

## [0.2.0]

### Added

- `parse(value, strict=True)` checks the RFC 9110 section 7.6.3 grammar and raises
  `ViaError`, a `ValueError` carrying the field line and offset.
- `parse` accepts several field lines (each read as its own list) and `None`.
- `append(existing, hop)` returns the value to forward, with `pseudonyms` to hide hosts
  and `drop_comments` to remove received comments.
- `has_loop(value, name, *names)` finds this proxy's own names in the chain.
- `Hop.host` and `Hop.port` (`None` when absent or above 65535).
- `python -m viaheader` and the `viaheader` command print the hops of values or of the
  Via lines of a header block as JSON.

### Changed

- An invalid entry is skipped and parsing resumes at the first comma after the point
  where it broke; an unclosed comment no longer swallows the entries after it.
- Text after the received-by or after the comment makes the entry invalid instead of
  being ignored.
- Comments are decoded: quoted-pairs are resolved and nested comments kept as text.
- `Hop` stores any spelling of the `HTTP` protocol name, and the empty string, as `HTTP`.
- `build` validates protocol, version and received-by, refuses control characters, and
  escapes backslashes and unpaired parentheses in comments.
- CR, LF and NUL in a value read as spaces in lenient mode.
- Parsing takes linear time, however many unclosed comments a value holds.

## [0.1.0]

- First release: parse and build the HTTP Via header per RFC 9110, with typed hops,
  an optional protocol name defaulting to HTTP, comment handling, and comma-aware
  splitting that never breaks inside a comment.
