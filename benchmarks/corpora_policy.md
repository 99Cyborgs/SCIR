# Corpora Policy
Status: Normative

## Targeted corpora

Use tier-labeled, subset-bounded corpora.

Preferred early corpora:

- Python subset functions and modules
- Rust safe-subset functions and modules
- TypeScript structured subset functions and modules

## Rules

- record dataset name and hash in the benchmark manifest,
- record language and tier mix,
- exclude unsupported-heavy corpora from support claims,
- do not use proprietary-only corpora for the primary evidence set,
- keep held-out data for Track `C` and repository repair tasks.

## Current executable corpus

The current executable harness is fixed to:

- `python-bootstrap-fixtures` for Track `A` and Track `B`,
- `python-bootstrap-fixtures` for Python `D-PY` Track `D`,
- `rust-bootstrap-fixtures` for Rust `N` Track `D`.

Broadening beyond those corpora requires a separate plan and must not weaken the existing benchmark doctrine.
