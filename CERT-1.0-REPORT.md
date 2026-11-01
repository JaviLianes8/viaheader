# viaheader 1.0.0 certification report

The 1.0.0 certification bar (19 items) applied to viaheader. PyPI has 0.2.0, which is
byte for byte the `main` branch at 09b74be (the wheel's modules compared with the tree), so
every change listed here is a change against the PyPI release.

Progress:
- [x] Branch `release/1.0.0` created from `main` (09b74be, same code as PyPI 0.2.0)
- [x] Baseline gates on 0.2.0
- [x] API review and 1.0.0 changes (item 1)
- [x] Errors, typing, docstrings and doctests (items 2 to 5)
- [x] Ground truth: specifications fetched live and hash-checked (item 7)
- [ ] Contract, fuzz and author mutation round (items 6, 9, 18)
- [x] Docs: README, GUIDE, CHANGELOG (items 11, 12; rendering check pending)
- [ ] Packaging, e2e and upgrade from PyPI 0.2.0, every Python (items 8, 10, 13, 14)
- [ ] Five QA lenses report PASS (item 19)
- [ ] Independent reviewer reports PASS (item 16)
- [ ] Gates (item 15), final run
- [ ] PR and trace guard CLEAN (item 17); merge and publish left to the maintainer

## Baseline and API review

On 2026-11-01 the PyPI JSON endpoint listed only 0.2.0. Its downloaded wheel's package
files match main at 09b74be. Baseline format, lint and strict typing passed; pytest:
225 passed, 9 skipped (eight unfetched source checks and one opt-in wheel test).

The six public names, signatures, defaults, header values and error families are
preserved. Rejected field values are no longer echoed in validation errors. Class
module names are public, and the accidental `annotations` attribute is removed.
CLI unknown arguments are omitted from errors and closed output pipes return 1.
Loop-name matching and CLI unfolding avoid quadratic work. All changes appear in
the 1.0.0 CHANGELOG, dated 2026-11-01; GUIDE describes the complete contracts.

Every exported name and Hop property now has runnable examples. Tests pin signatures,
frozen values, copying, pickling, error positions, iterable inputs and safe errors.

## Ground truth

Fetched 2026-11-01: RFC 9110, RFC 9112, RFC 3986 and the pinned MDN Via page. URLs,
revisions, sizes, SHA-256 and licenses are recorded in `tests/upstream/MANIFEST.json`.
All four live downloads match the pinned hashes. `scripts/fetch_upstream.py` can
place them outside the checkout with `VIAHEADER_UPSTREAM`; no fetched text is shipped.
The source tests extract real examples and ABNF rules before comparing the parser,
builder, character classes and ports. Hand-written contract and fuzz data are separate.
The README comparison with `str.split` and `email.message.Message` is executed in
`test_readme_comparison_with_split_and_email`.

## Pending verification

Wheel and sdist inspection, real installation and PyPI upgrade, interpreter matrix,
mutation round and final gates remain. Independent review and the five QA lenses
have not run; no verdict is claimed for items 16 or 19.
