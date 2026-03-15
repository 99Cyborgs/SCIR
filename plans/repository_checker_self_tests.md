# Repository Checker Self-Tests

Status: complete
Owner: Codex
Date: 2026-03-15

## Objective

Make the bootstrap repository checker exercise negative-path fixture tests under `--mode test` so repository contract checks are validated beyond the happy path.

## Scope

- refactor the repository checker so it can validate an explicit repository root
- add negative self-tests for missing required files, malformed report-schema requirements, and validator invariant drift
- keep the top-level command contract unchanged
- document the stronger `test` behavior

## Non-goals

- adding executable `SCIR-H` or `SCIR-L` validators
- changing SCIR semantics, schemas, or benchmark doctrine
- introducing a broad external test harness

## Touched files

- `plans/repository_checker_self_tests.md`
- `scripts/validate_repo_contracts.py`
- `README.md`

## Invariants that must remain true

- `make validate` remains the blocking repository validation command
- `make test` remains a bootstrap repository-check target
- no semantic, profile, preservation, or tier claims change
- repository checker failures remain blocking

## Risks

- self-tests could become brittle if they depend on incidental formatting
- repository copies used for self-tests could be slower than necessary if the fixture set grows

## Validation steps

- `python scripts/validate_repo_contracts.py --mode validate`
- `python scripts/validate_repo_contracts.py --mode test`
- `python scripts/benchmark_contract_dry_run.py`

## Rollback strategy

Remove the self-test routines and restore `--mode test` to the baseline repository contract checks only.

## Evidence required for completion

- repository checker supports validating an explicit root
- `--mode test` exercises negative fixtures and passes
- `README.md` reflects the stronger bootstrap test behavior

## Completion evidence

- `python scripts/validate_repo_contracts.py --mode validate` passed on 2026-03-15
- `python scripts/validate_repo_contracts.py --mode test` passed on 2026-03-15
- `python scripts/benchmark_contract_dry_run.py` passed on 2026-03-15
