# viaheader 1.0.0 certification report

Preparation and QA rounds 1, 2 and 3 corrections recorded on 2026-11-01.
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
- [x] QA round 2 workspace correction and supplemental contract checks
- [x] QA round 3 folded-comment contract and mutation verification
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
| 6 | PASS: 311 tests including package, CLI, failure paths, values and documentation |
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
| 18 | PASS: 28 preparation, 23 round 1 and 12 round 2 mutations killed; round 3 survivor now killed by CLI and wheel contracts |
| 19 | Round 3: e FAIL on missing folded-comment coverage, corrected below; prior workspace blocker resolved; independent re-review pending |

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

## QA lenses: round 2 corrections

Reviewed head: `c33100372732668d8c43dbf43bdc22717cd4c6e5`.
Fix commit: [`87b79ead6b0e8c52952b0f835d646eab7babeb65`](https://github.com/JaviLianes8/viaheader/commit/87b79ead6b0e8c52952b0f835d646eab7babeb65).
Report: `lens-e-r2/REPORT.md` under the certification scratch root.
The independent verdict was FAIL because its clone destination was already occupied;
it ran no tests or mutations. Independent same-lens re-verification remains pending.

| Finding | Correction |
| --- | --- |
| E-BLOCK-01 | Confirmed the existing clone has a modified `_headers.py`; left it untouched. Cloned the reviewed head into a newly allocated directory, reran contracts and mutations, and assigned a separate unused review destination with a collision fallback below. |

Supplemental evidence root:
`C:/lianes8-build/codex-pylib/scratch/viaheader-cert/fix-r2-1ce9ea3b58e54516aaa2ef119e7c2783/`.
The fresh clone started clean at the reviewed head. Twelve mutations ran serially,
one at a time, with bytecode disabled, a 300 s per-test timeout, and a 600 s run limit.
Original source hashes were checked after every restoration. These checks supplement
the correction; they do not constitute an independent lens-e verdict.

R2-10 initially survived both its targeted tests and the full suite. Two hand-written
contracts now cover string-subclass proxy names without a port or with an empty port.
Both failed with normalization removed and passed with the unchanged implementation.
There is no library behavior or API change, so no CHANGELOG entry is needed.
All twelve mutations were then caught by test failures, with no collection errors or
timeouts. Baseline and restored suites passed 308 tests with the two opt-in e2e tests
skipped. The release checkout passed all 310 tests with both e2e options enabled.

| Id | Mutation | Contract that failed (all KILLED after the added coverage) |
| --- | --- | --- |
| R2-01 | Decode header bytes as UTF-8 | `test_stdin_bytes_are_read_as_latin_1` |
| R2-02 | Keep fields from earlier responses | `test_the_last_response_of_a_redirect_chain_is_used` |
| R2-03 | Match header names case sensitively | `test_stdin_bytes_are_read_as_latin_1` |
| R2-04 | Discard folded Via continuations | `test_streaming_retains_last_response_and_ignores_forged_body_fields` |
| R2-05 | Read the whole remaining body for lookahead | `test_body_size_does_not_control_cli_memory` |
| R2-06 | Trust methods on single string subclasses | `test_parse_uses_underlying_field_line` |
| R2-07 | Trust methods on iterable string subclasses | `test_parse_uses_underlying_field_line` |
| R2-08 | Retain overridden methods in Hop fields | `test_serialization_rejects_hidden_injection` |
| R2-09 | Trust pseudonym subclass methods | `test_invalid_subclass_pseudonym_is_rejected_even_when_unused` |
| R2-10 | Trust proxy-name subclass methods | `test_subclass_proxy_names_without_a_port_use_underlying_length` |
| R2-11 | Reject the maximum port | `test_ports_are_tcp_port_numbers` |
| R2-12 | Shift error field-line indices | `test_invalid_values_raise_with_the_offset` |

Evidence files: `mutation-definitions.json`, `mutation-results.json`, `source-hashes.json`,
`R2-10-full.log`, `R2-10-regression-red.log`, and `verified-*.log` / `verified-*.xml`.
Format, lint, strict source typing and full pytest each exited 0 before committing.
Pytest temporary directories and build temporary files were confined to this evidence root.

### Independent lens-e handoff

Assigned unused destination:
`C:/lianes8-build/codex-pylib/scratch/viaheader-cert/lens-e-r2-independent-0df6f587b47148c89d3586a117730362/src`.
Neither this directory nor its parent was created by the correction checks.
The previously assigned `lens-e-r2/src` is retired from this handoff.
If the new destination is occupied when the review starts, allocate a fresh GUID-suffixed
directory under the same scratch root. Do not reuse, move, reset or delete existing work.
This replacement allocation is part of the assignment, so a collision does not block review.

```powershell
$scratch = 'C:/lianes8-build/codex-pylib/scratch/viaheader-cert'
$review = "$scratch/lens-e-r2-independent-0df6f587b47148c89d3586a117730362"
while (Test-Path -LiteralPath $review) {
    $review = "$scratch/lens-e-r2-independent-$([guid]::NewGuid().ToString('N'))"
}
New-Item -ItemType Directory -Path $review -ErrorAction Stop | Out-Null
git clone --branch release/1.0.0 https://github.com/JaviLianes8/viaheader "$review/src"
if ($LASTEXITCODE -ne 0) { throw 'Fresh review clone failed' }
git -C "$review/src" rev-parse HEAD
git -C "$review/src" status --porcelain
```

Verify the clone is clean and matches the pushed correction head before starting.
Record the actual workspace in the independent report. Keep its mutation definitions
independent of the supplemental table, run at least ten probes, use 300 s per test,
and keep all temporary files under the allocated review directory.

## QA lenses: round 3 corrections

Reviewed head: `07e6091657795250d7f7b3238fa7fdf142e20291`.
Fix commit: [`5b79529de8ec58fb0140211f6665cf0aa8815f24`](https://github.com/JaviLianes8/viaheader/commit/5b79529de8ec58fb0140211f6665cf0aa8815f24).
Report: `lens-e-r3/REPORT.md` under the certification scratch root.
The independent review resolved E-BLOCK-01 and killed nine of ten mutations, but
reported FAIL because M06 survived. Same-lens re-verification remains pending.

| Finding | Correction |
| --- | --- |
| E-CONTRACT-01 | Added exact nonbreaking-space preservation assertions through the public CLI subprocess and both installed-wheel CLI entry points. The reported continuation-trimming mutation now fails the CLI contract and wheel e2e test. |

The hand-written input is `b"Via: 1.1 edge (\r\n \xa0)\r\n\r\n"`; its decoded
comment must equal `" \u00a0"`, with exit status 0 and empty stderr. The current
implementation already meets this contract. Production code, API and behavior are
unchanged, so no CHANGELOG entry is needed.

In a fresh scratch copy, the new CLI test passed before mutation. Changing only
`raw.strip(" \t")` to `raw.strip()` made the CLI test and freshly built wheel test
fail their exact-comment assertions: actual `" "`, expected `" \u00a0"`. Both failures
were assertion failures, with successful CLI exits and empty stderr. Restoring the
original source bytes made the CLI regression pass again.

| Mutation | Result | Contracts that caught it |
| --- | --- | --- |
| Lens-e M06: trim all Unicode whitespace from folded continuations | KILLED | `test_folded_comment_preserves_nonbreaking_space`; `test_installed_wheel_end_to_end` |

Evidence root:
`C:/lianes8-build/codex-pylib/scratch/viaheader-cert/fix-r3-64a63c7a25034490805f05fac5184cdb/`.
`verify_mutation.py`, `mutation-results.json`, `baseline.log`, `M06-cli-red.log`,
`M06-wheel-red.log`, `restored.log` and matching XML files record the probe and source
hash. Temporary files stayed under this root; every pytest run used a 300 s per-test
timeout. No pre-existing review workspace was modified.

All four gates exited 0: `ruff format --check .`, `ruff check .`, `mypy --strict src`
and `pytest`. Strict typing of tests also passed. With fetched reference files and
both wheel and PyPI upgrade checks enabled, the full suite passed all 311 tests with
no skips. Gate outputs are in `format.log`, `lint.log`, `types.log`, `pytest.log`,
`gate-results.json` and `full-pytest.xml` under the evidence root.

## Disputed findings

None.
