# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0]

### Added

- `parse(value, strict=True)` checks the RFC 9110 section 7.6.3 grammar and raises
  `ViaError`, a `ValueError` carrying the field line and offset.
- `parse` accepts several field lines (each read as its own list) and `None`.
- `append(existing, hop)` returns the value to forward, with `pseudonyms` to hide hosts
  and `drop_comments` to remove received comments.
- `has_loop(value, name, *names)` finds this proxy's own names in the chain.
- `Hop.host` and `Hop.port`.
- `python -m viaheader` and the `viaheader` command print the hops of values or of the
  Via lines of a header block as JSON.

### Changed

- An invalid entry is skipped and parsing resumes at the first comma after the point
  where it broke; an unclosed comment no longer swallows the entries after it.
- Text after the received-by or after the comment makes the entry invalid instead of
  being ignored.
- Comments are decoded: quoted-pairs are resolved and nested comments kept as text.
- The `HTTP` protocol name is recognised whatever its case.
- `build` validates protocol, version and received-by, refuses control characters, and
  escapes backslashes and unpaired parentheses in comments.
- CR, LF and NUL in a value read as spaces in lenient mode.

## [0.1.0]

- First release: parse and build the HTTP Via header per RFC 9110, with typed hops,
  an optional protocol name defaulting to HTTP, comment handling, and comma-aware
  splitting that never breaks inside a comment.
