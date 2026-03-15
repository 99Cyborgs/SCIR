# Benchmark Checker Self-Tests

Status: complete
Owner: Codex
Date: 2026-03-15

## Objective

Strengthen the benchmark doctrine dry-run checker so it validates an explicit repository root and exercises negative-path self-tests without changing the top-level benchmark command contract.

## Scope

- refactor the benchmark checker so it can validate an explicit repository root
- add benchmark-doctrine checks for contamination controls and benchmark schema structure
- add negative self-tests for missing track markers, missing gate markers, and malformed benchmark schema requirements
- document the stronger dry-run behavior

## Non-goals

- adding an executable benchmark harness
- changing benchmark doctrine semantics, tracks, baselines, or kill gates
- changing non-benchmark repository validation behavior

## Touched files

- `plans/benchmark_checker_self_tests.md`
- `scripts/benchmark_contract_dry_run.py`
- `README.md`
- `ci/benchmark_pipeline.md`

## Invariants that must remain true

- `make benchmark` remains the single top-level benchmark entry point
- benchmark doctrine remains documentation-first and contract-first
- no new benchmark claims are introduced
- strong-baseline and contamination-control doctrine remain mandatory

## Risks

- the checker could become too brittle if it keys off incidental wording instead of contractual markers
- benchmark self-tests could slow the dry run if the fixture set grows carelessly

## Validation steps

- `python scripts/validate_repo_contracts.py --mode validate`
- `python scripts/validate_repo_contracts.py --mode test`
- `python scripts/benchmark_contract_dry_run.py`

## Rollback strategy

Remove the self-test routines and return the benchmark checker to direct doctrine marker checks only.

## Evidence required for completion

- benchmark checker supports validating an explicit root
- benchmark checker self-tests pass
- command-facing docs reflect the stronger benchmark dry-run behavior

## Completion evidence

- `python scripts/validate_repo_contracts.py --mode validate` passed on 2026-03-15
- `python scripts/validate_repo_contracts.py --mode test` passed on 2026-03-15
- `python scripts/benchmark_contract_dry_run.py` passed on 2026-03-15
