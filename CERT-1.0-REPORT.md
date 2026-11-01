# viaheader 1.0.0 certification report

Preparation and QA round 1 corrections recorded on 2026-11-01.
Independent re-review, merge and publication remain pending.

Progress:
- [x] Resume `release/1.0.0`, preserving the initial report commit 4e2cb17
- [x] Baseline gates and PyPI 0.2.0 comparison
- [x] Stable API, exact exports, runnable examples, typing and errors (items 1 to 5)
- [x] Contracts, fetched ground truth, seeded properties and mutations (items 6, 7, 9, 18)
- [x] Wheel installation, CLI, PyPI upgrade and distribution inspection (items 8, 13, 14)
- [x] Final interpreter matrix (item 10): eight installed-wheel environments
- [x] README, GUIDE, dated CHANGELOG and rendering check (items 11, 12)
- [x] Four gates, plus strict typing of tests (item 15)
- [ ] Independent reviewer (item 16)
- [x] QA round 1 corrections and regression checks
- [ ] Five independent QA PASS verdicts (item 19)
- [x] PR #3 and guard CLEAN; merge and publication remain pending (item 17)

## Scorecard

| Item | Result and evidence |
| --- | --- |
| 1 | PASS: six public names, signatures and defaults pinned; all changes in CHANGELOG |
| 2 | PASS: `__all__` matches the public namespace; documentation imports only public names |
| 3 | PASS: all six names and both Hop properties have executed doctests; README and GUIDE run |
| 4 | PASS: `mypy --strict src tests`, runtime annotations, installed consumer, shipped `py.typed` |
| 5 | PASS: typed errors and positions; rejected values omitted, type names bounded |
| 6 | PASS: 308 tests including package, CLI, failure paths, values and documentation |
| 7 | PASS: four sources fetched live, hashed and used to derive examples and grammar checks |
| 8 | PASS: fresh wheel installation, both CLI entry points, real pipe, in-place PyPI upgrade |
| 9 | PASS: four seeded properties, bounded grammar oracle, hostile-size and nesting tests |
| 10 | Preparation PASS: eight builds, Python 3.10 to 3.14; fixes checked on 3.14.6 |
| 11 | PASS: problem, verified alternatives, absolute links, exact badge, strict twine check |
| 12 | PASS: `1.0.0` CHANGELOG dated 2026-11-01 |
| 13 | PASS: version 1.0.0, Production/Stable, Python 3.10 to 3.14, MIT, URLs, no runtime dependencies |
| 14 | PASS: wheel and sdist inspected; license and types present, no fetched text or scratch files |
| 15 | PASS: four commands each exit 0 independently; full opt-in suite has no skips |
| 16 | PENDING: independent review has not run |
| 17 | READY: PR #3 from `release/1.0.0`, guard CLEAN; merge and publication pending |
| 18 | PASS: 28 preparation mutations and 23 correction-round mutations killed |
| 19 | Round 1: a FAIL, c FAIL, e BLOCKED; corrections below await independent re-review |

## Preparation evidence

The complete preparation details, distribution hashes and interpreter matrix remain
in the [baseline report](https://github.com/JaviLianes8/viaheader/blob/77b903ed1a7fb7d385921bbef28fee84d6e47674/CERT-1.0-REPORT.md).
The following records describe that preparation, before the QA fixes below.

PyPI 0.2.0 matched main at 09b74be byte for byte. Baseline gates passed with
225 tests passing and 9 skipped. Public names, signatures and defaults remain pinned
by contracts for values, hashing, copying, pickling, properties, iterables and errors.
Hop is frozen and defers syntax validation. CHANGELOG lists every behavior change.

Four references fetched on 2026-11-01 matched `tests/upstream/MANIFEST.json`:
RFC 9110, RFC 9112, RFC 3986 and the pinned MDN Via revision. Their URLs, revisions,
sizes, hashes and licenses are recorded there. Downloaded text is neither committed
nor shipped. `scripts/fetch_upstream.py` reproduces the downloads outside the checkout.
Source tests extract examples and grammar; a separate bounded grammar checks
30,000 generated strings. Four seeded properties each exercise 3,000 cases.
Hand-written cases are not presented as official vectors. Hostile tests cover
256 KiB shapes, depth 131,072, huge ports and fields, and 20,000 names against hops.

The preparation suite passed 273 tests with wheel and PyPI upgrade checks enabled.
Fresh venvs imported the installed wheel in isolated mode, drove both CLI entrypoints,
and checked real pipes. An in-place upgrade from PyPI 0.2.0 preserved 25,007 snapshot
results and bidirectional pickles. An external strict typed consumer passed.
Wheel and sdist contents, licenses, type marker and exclusions were checked;
both artifacts passed `twine check --strict`. Original hashes are in the baseline report.

The preparation matrix used the wheel and sdist matching e08eef5, with source imports
disabled: 271 passed and 2 opt-in tests skipped on each of CPython 3.10.22, 3.11.11
(Blender), 3.11.18, 3.12.16, 3.13.18, 3.14.6, 3.14.10 and 3.14.10 free-threaded.
Stale launcher entries pointed to absent executables; working builds were found on disk.
This correction round ran on CPython 3.14.6; it does not renew the full matrix verdict.

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
The correction suite passed 308 tests with fetched sources, wheel checks and PyPI
upgrade enabled. Independent review (16), merge/publication (17) and five QA PASS
verdicts (19) remain pending; no pass is claimed for those stages.

PR: https://github.com/JaviLianes8/viaheader/pull/3, titled `viaheader 1.0.0`,
from `release/1.0.0` to `main`. The guard reports `CLEAN: viaheader #3`.

## QA lenses: round 1 corrections

Reviewed head: `77b903ed1a7fb7d385921bbef28fee84d6e47674`.
Fix commit: [`5becf580c59ca3fc7db8ac1042d7d5d797fda52b`](https://github.com/JaviLianes8/viaheader/commit/5becf580c59ca3fc7db8ac1042d7d5d797fda52b).
Reports: `lens-a-r1/REPORT.md`, `lens-c-r1/REPORT.md`, `lens-e-r1/REPORT.md` under
`C:/lianes8-build/codex-pylib/scratch/viaheader-cert/`. Their recorded verdicts are
FAIL, FAIL and BLOCKED respectively. No new independent verdict is claimed here.

| Finding | Correction |
| --- | --- |
| A-001 | README and GUIDE describe incremental reads, body-prefix lookahead, buffering and header-only EOF. |
| A-002 | README explicitly allows HTAB in comments while rejecting other forbidden controls. |
| A-003 | README and build docstring qualify equality for lists and explain iterator consumption. |
| C-01 | Normalize Hop fields, pseudonym keys/values and proxy names to underlying built-in strings. |
| C-02 | Normalize single and iterable field lines before scanning; diagnostics contain one character. |
| C-03 | Stream binary and text stdin; stop at a body prefix, preserving last-response selection. |
| E-BLOCK-01 | Fresh clone and serial mutation rerun completed; existing workspace untouched. Independent rerun assigned below. |

All behavior changes are in CHANGELOG. Contracts were added before implementation:
`tests/test_string_subclasses.py` and `tests/test_cli_streaming.py` produced 23 failures
and 12 passes at the reviewed head; all 35 now pass. The wider targeted run passed 159.
The reviewer's seven regressions and memory probe were copied to fresh scratch and
replayed unchanged against the fixed source, with only their paths redirected: 8 passed.
For 0, 1, 4 and 16 MiB bodies, CLI peak working sets were 18,378,752, 18,362,368,
18,305,024 and 18,247,680 bytes. The new stream contracts also bound reads and allocations.
Format, lint, strict source typing and full pytest each exited 0; strict test typing passed.

Evidence root: `C:/lianes8-build/codex-pylib/scratch/viaheader-cert/fix-r1-20261101-ec57/`.
Logs: `evidence/regressions-red.txt`, `evidence/reviewer-replay.txt`, `evidence/full-suite.txt`.
Mutation evidence: `mutation-definitions.json`, `mutation-results.json`, per-case XML/logs.
The fresh clone began at the reviewed head, then received the fixes. Each mutation ran
alone, with bytecode disabled, 300 s per test and source hashes checked after restoration.
Baseline and restored suites each passed 306 tests, with only the 2 opt-in e2e tests skipped.
R1-03 survived its narrow selection but failed the full suite; no mutation survived.
These are supplemental checks, not a substitute for independent lens-e sign-off.

| Id | Mutation | Contract that failed (all KILLED) |
| --- | --- | --- |
| R1-01 | Drop the final parsed hop | `test_a_version_alone_means_http` |
| R1-02 | Shift field-line error index | `test_invalid_values_raise_with_the_offset` |
| R1-03 | Merge independent field lines | `test_the_error_names_the_field_line` |
| R1-04 | Keep lowercase HTTP unnormalized | `test_any_spelling_of_http_is_omitted` |
| R1-05 | Reject the maximum port | `test_ports_are_tcp_port_numbers` |
| R1-06 | Treat port zero as a wildcard | `test_empty_port_is_a_wildcard_and_zero_is_a_specific_port` |
| R1-07 | Prepend the new hop | `test_append_keeps_the_received_order` |
| R1-08 | Keep received comments when dropping them | `test_drop_comments_removes_received_comments_only` |
| R1-09 | Make host matching case sensitive | `test_pseudonyms_replace_the_whole_received_by` |
| R1-10 | Accept unused invalid pseudonyms | `test_all_names_and_mappings_are_validated_before_reading_input` |
| R1-11 | Stop escaping unmatched parentheses | `test_comments_are_escaped_only_where_needed` |
| R1-12 | Build legacy IPv6 as strict output | `test_an_invalid_received_by_is_refused` |
| R1-13 | Lose strict invalid-character precedence | `test_invalid_values_raise_with_the_offset` |
| R1-14 | Accept comments without whitespace in strict mode | `test_invalid_values_raise_with_the_offset` |
| R1-15 | Swap parsed version and protocol | `test_a_version_alone_means_http` |
| R1-16 | Retain quoted-pair backslashes | `test_a_comment_is_decoded` |
| R1-17 | Lose empty comments | `test_an_empty_comment_is_an_empty_string` |
| R1-18 | Remove parse from exports | `test_all_lists_exactly_the_public_api` |
| R1-19 | Trust subclass serialization fields | `test_serialization_rejects_hidden_injection` |
| R1-20 | Trust subclass scanning methods | `test_parse_uses_underlying_field_line` |
| R1-21 | Buffer the ignored body through EOF | `test_body_size_does_not_control_cli_memory` |
| R1-22 | Retain earlier response fields | `test_streaming_retains_last_response_and_ignores_forged_body_fields` |
| R1-23 | Break the validation error family | `test_via_error_is_a_value_error` |

E-BLOCK-01 handoff: a new empty directory is reserved at
`C:/lianes8-build/codex-pylib/scratch/viaheader-cert/lens-e-r1-independent-20261101-ec57/`.
Its `src` destination is absent and ready for a fresh clone of the pushed correction head.
The independent mutation round and same-lens re-verification remain with the release
review; no pre-existing mutation workspace was moved, reset, deleted or reused.

## Disputed findings

None.
