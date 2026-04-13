# Repo Documentation Batch 4

Status: complete
Owner: Codex
Date: 2026-04-13

## Objective

Add comment-only documentation to `scripts/benchmark_contract_dry_run.py` so its benchmark-doctrine checks, report assembly, and self-test harness are readable without changing behavior.

## Scope

- Add a normalized file header to `scripts/benchmark_contract_dry_run.py`
- Add function docstrings and selective inline comments in these sections:
  - helper and schema-validation entrypoints
  - benchmark-doc and Track C contract checks
  - comparison-summary and report-building helpers
  - output writing, self-tests, and CLI entrypoint
- Keep mutation fixtures and benchmark semantics behaviorally unchanged

## Non-goals

- No logic changes, refactors, renames, or benchmark-policy changes
- No edits to `scripts/validate_repo_contracts.py` in this batch
- No schema or report-surface changes

## Touched files

- `plans/2026-04-13-repo-documentation-batch-4.md`
- `scripts/benchmark_contract_dry_run.py`

## Invariants that must remain true

- The benchmark dry-run script remains behaviorally identical
- Benchmark checks, claim report generation, and self-test failures remain byte-for-byte compatible in meaning
- The script must still pass syntax lint and the canonical repo validation gate

## Risks

- The file is large and mixes doctrine checks, report generation, and negative fixtures, so comments can become noisy if they merely narrate mechanics
- Import-time dependencies from `validate_repo_contracts.py` and pipeline helpers mean inaccurate prose here would mislead readers about real authority boundaries

## Validation steps

- `python scripts/run_repo_lint.py`
- `python scripts/run_repo_validation.py`

## Rollback strategy

Revert only the documentation edits in `scripts/benchmark_contract_dry_run.py` if review or validation reveals any mismatch between the prose and the actual benchmark flow.

## Evidence required for completion

- Diff review confirming comment-only edits in `scripts/benchmark_contract_dry_run.py`
- `python scripts/run_repo_lint.py` passed on 2026-04-13
- `python scripts/run_repo_validation.py` passed on 2026-04-13
