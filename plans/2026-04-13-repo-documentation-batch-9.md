# Repo Documentation Batch 9

Status: complete
Owner: Codex
Date: 2026-04-13

## Objective

Add comment-only documentation to the repo-root, corpus-validation, import-bundle, and case-validation slice of `scripts/scir_bootstrap_pipeline.py` so the artifact-validation layer is readable without changing behavior.

## Scope

- Add docstrings for:
  - repo root and JSON/schema loading helpers
  - fixture and artifact naming helpers
  - negative corpus validation helpers
  - import-bundle schema and boundary-contract validation
  - `validate_scirh_case`
  - `validate_scirhc_case`
- Add narrow inline comments only where retained validator-code or negative-corpus intent would otherwise be easy to misread

## Non-goals

- No logic changes, refactors, renames, or pipeline stage changes
- No edits to lowering, Wasm emission, reconstruction, benchmark tracks, or Rust sections in this batch
- No validator, schema, or artifact-contract changes

## Touched files

- `plans/2026-04-13-repo-documentation-batch-9.md`
- `scripts/scir_bootstrap_pipeline.py`

## Invariants that must remain true

- Negative `SCIR-H` and `SCIR-L` corpora must still fail with their expected diagnostic-code families
- Import-bundle validation must remain schema-driven and boundary-contract aware
- `SCIR-Hc` validation must remain derived-only and report-scoped

## Risks

- GitNexus reported `validate_scirh_case` as `CRITICAL` because `run_pipeline`, `run_self_tests`, sweep, and benchmark dry-run surfaces depend on it
- This slice emits retained validation artifacts, so inaccurate comments could misstate report-contract behavior

## Validation steps

- `python -m py_compile G:\GitHub\incubate\SCIR\scripts\scir_bootstrap_pipeline.py`
- `python scripts/run_repo_lint.py`
- `python scripts/run_repo_validation.py`

## Rollback strategy

Revert only the documentation edits in `scripts/scir_bootstrap_pipeline.py` and this historical batch plan if review finds any mismatch between the prose and actual case-validation behavior.

## Evidence required for completion

- Diff review confirming comment-only edits in the artifact-validation slice of `scripts/scir_bootstrap_pipeline.py`
- GitNexus impact recorded for `validate_scirh_case` on 2026-04-13 and treated as a comment-only critical-sensitivity surface
- `python -m py_compile G:\GitHub\incubate\SCIR\scripts\scir_bootstrap_pipeline.py` passed on 2026-04-13
- `python scripts/run_repo_lint.py` passed on 2026-04-13
- `python scripts/run_repo_validation.py` passed on 2026-04-13
