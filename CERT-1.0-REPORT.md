# viaheader 1.0.0 certification report

Preparation evidence recorded on 2026-11-01. Independent review, five QA lenses,
merge and publication remain pending.

Progress:
- [x] Resume `release/1.0.0`, preserving the initial report commit 4e2cb17
- [x] Baseline gates and PyPI 0.2.0 comparison
- [x] Stable API, exact exports, runnable examples, typing and errors (items 1 to 5)
- [x] Contracts, fetched ground truth, seeded properties and mutations (items 6, 7, 9, 18)
- [x] Wheel installation, CLI, PyPI upgrade and distribution inspection (items 8, 13, 14)
- [ ] Final interpreter matrix (item 10)
- [x] README, GUIDE, dated CHANGELOG and rendering check (items 11, 12)
- [x] Four gates, plus strict typing of tests (item 15)
- [ ] Independent reviewer (item 16)
- [ ] Five independent QA lenses (item 19)
- [ ] PR and guard; merge and publication remain pending (item 17)

## Scorecard

| Item | Result and evidence |
| --- | --- |
| 1 | PASS: six public names, signatures and defaults pinned; all changes in CHANGELOG |
| 2 | PASS: `__all__` matches the public namespace; documentation imports only public names |
| 3 | PASS: all six names and both Hop properties have executed doctests; README and GUIDE run |
| 4 | PASS: `mypy --strict src tests`, runtime annotations, installed consumer, shipped `py.typed` |
| 5 | PASS: typed errors and positions; rejected values omitted, type names bounded |
| 6 | PASS: 273 tests including package, CLI, failure paths, values and documentation |
| 7 | PASS: four sources fetched live, hashed and used to derive examples and grammar checks |
| 8 | PASS: fresh wheel installation, both CLI entry points, real pipe, in-place PyPI upgrade |
| 9 | PASS: four seeded properties, bounded grammar oracle, hostile-size and nesting tests |
| 10 | PENDING: final installed-wheel matrix in progress |
| 11 | PASS: problem, verified alternatives, absolute links, exact badge, strict twine check |
| 12 | PASS: `1.0.0` CHANGELOG dated 2026-11-01 |
| 13 | PASS: version 1.0.0, Production/Stable, Python 3.10 to 3.14, MIT, URLs, no runtime dependencies |
| 14 | PASS: wheel and sdist inspected; license and types present, no fetched text or scratch files |
| 15 | PASS: four commands each exit 0 independently; full opt-in suite has no skips |
| 16 | PENDING: independent review has not run |
| 17 | PENDING: PR and guard at handoff; merge and publication are separate |
| 18 | PASS: 28 deliberate mutations, 28 killed, no survivors |
| 19 | PENDING: no lens verdicts recorded |

## Baseline and API review

The live endpoint https://pypi.org/pypi/viaheader/json listed only 0.2.0 on
2026-11-01. Every package file in its downloaded wheel matches main at 09b74be
byte for byte. Baseline format, lint and strict typing passed; pytest was
225 passed, 9 skipped (eight unfetched source checks and one opt-in wheel test).

The six names and signatures remain: `Hop(received_by, version, protocol="HTTP",
comment=None)`, `ViaError(message, *, line=None, position=None)`,
`parse(value, *, strict=False)`, `build(hops)`,
`append(existing, hop, *, pseudonyms=None, drop_comments=False)` and
`has_loop(value, name, *names)`. Hop remains a frozen dataclass with deferred syntax
validation. Contracts include values, hashing, copying, pickling, properties,
iterable inputs, ordering, pseudonyms, error families and exact parsing positions.

Changes checked against 0.2.0: validation no longer echoes entire field values;
wrong-type messages omit or bound type names; non-mapping pseudonyms consistently
raise TypeError instead of being ignored when falsy or raising AttributeError.
Hop and ViaError have the public module name, old and new pickles work both ways,
and the incidental `annotations` attribute is removed. CLI usage errors omit invalid
argument values. Closed stdout pipes return 1, including Windows EINVAL and flush
failures. Loop-name matching and header unfolding avoid quadratic work. All changes
are listed in CHANGELOG; parsed and serialized valid values remain unchanged.

## Ground truth and properties

Fetched on 2026-11-01: https://www.rfc-editor.org/rfc/rfc9110.txt,
https://www.rfc-editor.org/rfc/rfc9112.txt,
https://www.rfc-editor.org/rfc/rfc3986.txt and the MDN Via page at the immutable
revision recorded in `tests/upstream/MANIFEST.json`. The manifest records each URL,
revision, size, SHA-256 and license. All four live downloads match their hashes.
`scripts/fetch_upstream.py` re-fetches them; `VIAHEADER_UPSTREAM` can locate them
outside the checkout. Fetched text is neither committed nor shipped.

`test_sources.py` extracts the real Via examples and ABNF rules, checks tokens and
comment code points, quoted-pairs, ports, empty list members and folding. The MDN
examples also match. `test_grammar_property.py` builds a separate regex grammar
from fetched character classes and whitespace rules: three seeds, 10,000 candidate
strings each, with comment depth bounded to four. Inputs beyond that bound are
excluded from this oracle, while the nested-comment tests exercise depth 131,072.
Hand-written examples and generated cases are not presented as official vectors.
The README comparison with `str.split` and `email.message.Message` runs in a test.

Four seeded properties each generate 3,000 cases: safe recovery before appended
hops, loop detection, lenient forwarding and strict build/parse round trips.
Hostile tests cover nine 256 KiB shapes, deep nesting, many matched comments,
5,000-digit ports, 13 MB invalid fields, 40,000 continuation lines and 20,000 proxy
names against 20,000 hops. Tests have a 300 s limit. Error messages remain bounded;
input processing uses linear scans or indexed name lookup.

## Packaging and upgrade

The final full suite on CPython 3.14.6 has 273 passed, no skips, with both
`VIAHEADER_E2E=1` and `VIAHEADER_E2E_PYPI=1`. The wheel is installed into fresh venvs
and imported from an empty directory with `-I`; package location is asserted.
Both `python -m viaheader` and the console entry point run by subprocess, including
stdin header blocks, strict rejection and a real closed stdout pipe.

The actual PyPI 0.2.0 is installed first, exercised, then upgraded in place.
`upgrade_snapshot.py` compares 25,007 results across the releases: strict and lenient
parsing, building, forwarding, loop checks and error types/positions. Every result
matches; changed error text is checked separately. Hop and ViaError pickle round
trips work in both directions. A strict external typed consumer also passes.

The wheel contains only the package, `py.typed`, entry-point metadata and MIT
license. The sdist contains source, reproducible tests, source manifest, documentation
and scripts, without certification reports, downloaded references or caches.
Both artifacts pass `twine check --strict`. SHA-256:

- Wheel: `8e501d81a9c594f2221c597695dd76219e1b52485c4c7cf0fede692767c4503e`
- Sdist: `c402de4d11b0d58562913dc49b6a66786db7ed5ad8fc668c4c6f4c0c79d637c7`

## Author mutation round

Each mutation was applied alone in an isolated copy with bytecode writes disabled,
then restored. The contract suite ran with `-x`, a 300 s per-test limit and a 360 s
per-run limit. M27 and M28 enabled the wheel test and were caught by real installed
CLI execution. All 28 failed an assertion or expected-exception contract, with no
collection failures, timeouts or survivors. The unmodified full suite passed after.

| Id | Mutation | Result | Test that caught it |
| --- | --- | --- | --- |
| M01 | Reject port 65535 (`_model.py`) | KILLED | `test_limits.py::test_ports_are_tcp_port_numbers` |
| M02 | Do not trim leading port zeros (`_model.py`) | KILLED | `test_limits.py::test_a_port_with_many_leading_zeros_is_read` |
| M03 | HTTP normalization becomes case sensitive (`_model.py`) | KILLED | `test_build.py::test_any_spelling_of_http_is_omitted` |
| M04 | Accept invalid protocol version (`_build.py`) | KILLED | `test_build.py::test_an_invalid_version_is_refused` |
| M05 | Accept invalid received-by (`_build.py`) | KILLED | `test_build.py::test_an_invalid_received_by_is_refused` |
| M06 | Allow control characters in built comments (`_build.py`) | KILLED | `test_build.py::test_a_comment_a_field_value_cannot_carry_is_refused` |
| M07 | Do not escape unmatched opening parentheses (`_build.py`) | KILLED | `test_build.py::test_comments_are_escaped_only_where_needed` |
| M08 | Echo a rejected protocol version (`_build.py`) | KILLED | `test_safe_errors.py::test_invalid_fields_are_not_echoed` |
| M09 | Strict parser allows adjacent comments (`_scan.py`) | KILLED | `test_grammar_property.py::test_strict_parser_agrees_with_reference_grammar` |
| M10 | Do not blank CR LF and NUL (`_scan.py`) | KILLED | `test_parse.py::test_cr_lf_and_nul_become_spaces_when_lenient` |
| M11 | Skip the strict character precheck (`_scan.py`) | KILLED | `test_strict.py::test_invalid_values_raise_with_the_offset` |
| M12 | Do not recover after malformed entries (`_scan.py`) | KILLED | `test_cli.py::test_lenient_mode_skips_what_strict_mode_rejects` |
| M13 | Lowercase comment contents (`_comment.py`) | KILLED | `test_docs.py::test_every_readme_example_runs_and_prints_its_comment` |
| M14 | Keep quoted-pair backslashes (`_comment.py`) | KILLED | `test_build.py::test_comments_are_escaped_only_where_needed` |
| M15 | Prepend the new hop (`_forward.py`) | KILLED | `test_docs.py::test_every_readme_example_runs_and_prints_its_comment` |
| M16 | Ignore drop_comments (`_forward.py`) | KILLED | `test_forward.py::test_drop_comments_removes_received_comments_only` |
| M17 | Case-sensitive loop and pseudonym matching (`_forward.py`) | KILLED | `test_docs.py::test_every_readme_example_runs_and_prints_its_comment` |
| M18 | Ignore names with numerical ports (`_forward.py`) | KILLED | `test_forward.py::test_a_name_with_a_port_matches_only_that_port` |
| M19 | Ignore pseudonym replacement (`_forward.py`) | KILLED | `test_docs.py::test_every_readme_example_runs_and_prints_its_comment` |
| M20 | Report the wrong field-line index (`_parse.py`) | KILLED | `test_strict.py::test_the_error_names_the_field_line` |
| M21 | Discard the error offset (`_errors.py`) | KILLED | `test_docs.py::test_every_readme_example_runs_and_prints_its_comment` |
| M22 | Accept an empty token (`_chars.py`) | KILLED | `test_build.py::test_an_invalid_received_by_is_refused` |
| M23 | Retain Via from earlier responses (`_cli.py`) | KILLED | `test_cli_input.py::test_the_last_response_of_a_redirect_chain_is_used` |
| M24 | Echo unknown command-line arguments (`_cli.py`) | KILLED | `test_safe_errors.py::test_unknown_options_are_not_echoed` |
| M25 | Accept non-mapping pseudonyms (`_forward.py`) | KILLED | `test_safe_errors.py::test_pseudonyms_requires_a_mapping` |
| M26 | Echo unexpected option values (`_cli.py`) | KILLED | `test_safe_errors.py::test_unexpected_option_values_are_not_echoed` |
| M27 | Do not handle Windows closed output pipes (`_cli.py`) | KILLED | `test_e2e_wheel.py::test_installed_wheel_end_to_end` |
| M28 | Omit the protected stdout flush (`_cli.py`) | KILLED | `test_e2e_wheel.py::test_installed_wheel_end_to_end` |

## Gates and remaining review

Each command ran independently and exited 0: `ruff format --check .`, `ruff check .`,
`mypy --strict src`, `pytest`. The stronger `mypy --strict src tests` also passed.
The full pytest result above includes fetched sources, built-wheel checks and PyPI
upgrade. Independent review (16), merge/publication (17) and five fresh QA lenses
(19) remain pending; no pass verdict is claimed for those stages.
