# Repo Documentation Batch 1

Status: complete
Owner: Codex
Date: 2026-04-13

## Objective

Add comment-only documentation to a first high-value batch of executable Python modules so their role, invariants, and safe modification boundaries are explicit without changing behavior.

## Scope

- Add module headers, function or class docstrings, and selective inline comments to the first documentation batch:
  - `_internal/scirhc_transform.py`
  - `validators/scirhc_validator.py`
  - `scripts/benchmark_audit_common.py`
  - `scripts/benchmark_repro.py`
  - `scripts/run_repo_validation.py`
  - `scripts/run_repo_lint.py`
- Normalize terminology around canonical `SCIR-H`, derived `SCIR-Hc`, benchmark claim boundaries, and validation orchestration.
- Keep edits comment-only and syntax-safe.

## Non-goals

- No logic changes, refactors, renames, or formatting-only churn.
- No spec, schema, validator-behavior, benchmark-policy, or command-contract changes.
- No blanket repo-wide annotation of trivial fixture files in this batch.

## Touched files

- `plans/2026-04-13-repo-documentation-batch-1.md`
- `_internal/scirhc_transform.py`
- `validators/scirhc_validator.py`
- `scripts/benchmark_audit_common.py`
- `scripts/benchmark_repro.py`
- `scripts/run_repo_validation.py`
- `scripts/run_repo_lint.py`

## Invariants that must remain true

- Runtime behavior and public interfaces remain unchanged.
- Comments must stay evidence-based and aligned with the normative repo vocabulary.
- No canonical-storage or benchmark-governance semantics are widened by documentation text.
- All edited Python files must continue to parse cleanly.

## Risks

- Over-commenting low-complexity helpers could reduce signal-to-noise.
- Misstating governance or derivation intent would be worse than leaving code undocumented.
- `scripts/benchmark_audit_common.py` has medium import fan-in, so noisy edits there would raise review cost.

## Validation steps

- `python scripts/run_repo_lint.py`
- `python -m unittest discover -s tests -p test_scirhc_doctrine.py`

## Rollback strategy

Revert only the comment additions in the touched files if validation fails or review shows inaccurate intent statements.

## Evidence required for completion

- Diff review confirming comment-only edits across `_internal/scirhc_transform.py`, `validators/scirhc_validator.py`, `scripts/benchmark_audit_common.py`, `scripts/benchmark_repro.py`, `scripts/run_repo_validation.py`, and `scripts/run_repo_lint.py`
- `python scripts/run_repo_lint.py` passed on 2026-04-13
- `python -m unittest discover -s tests -p test_scirhc_doctrine.py` passed on 2026-04-13
- `python scripts/run_repo_validation.py` passed on 2026-04-13
