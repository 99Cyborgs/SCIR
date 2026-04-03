# 2026-04-01 Q-06-007 Distinguish Editorial Track C Sample Refreshes

Status: complete
Owner: Codex
Date: 2026-04-01

## Objective

Make the narrow set of editorial-only Track `C` sample refreshes explicit so formatting-only refreshes remain allowed while posture-changing sample edits stay governance-gated.

## Scope

- add explicit editorial-only Track `C` sample refresh allowances to shared benchmark metadata
- mirror those allowances in machine-checkable benchmark doctrine sections
- make benchmark and repo validation fail if the editorial-only boundary drifts
- add negative self-tests for Track `C` editorial-only refresh doctrine drift
- record the governance decision and advance the queue to the next non-default Track `C` follow-on

## Non-goals

- no change to the default benchmark gate
- no broader repair corpus
- no new Track `C` runner or schema
- no weakening of the retained pilot's sample-sync or re-decision rules

## Touched files

- `BENCHMARK_STRATEGY.md`
- `benchmarks/README.md`
- `benchmarks/tracks.md`
- `scripts/benchmark_contract_metadata.py`
- `scripts/benchmark_contract_dry_run.py`
- `scripts/validate_repo_contracts.py`
- `DECISION_REGISTER.md`
- `EXECUTION_QUEUE.md`
- `reports/exports/decision_register.export.json`
- `reports/exports/execution_queue.export.json`
- `plans/2026-04-01-mvp-narrowing-and-contract-hardening.md`

## Invariants that must remain true

- Track `A` and Track `B` remain the only default executable benchmark gates
- the Track `C` pilot remains explicit opt-in only
- `c_opaque_call` remains boundary-accounting-only
- the retained Track `C` pilot still uses the fixed Python repair corpus
- Track `C` sample artifacts remain illustrative and non-default

## Risks

- “editorial-only” can be interpreted too broadly unless the allowance list stays narrow and machine-checkable
- the editorial-only rule can accidentally conflict with the existing sample-sync equality contract if it is phrased imprecisely
- queue and decision exports can drift if not regenerated with the markdown updates

## Validation steps

- `python scripts/benchmark_contract_dry_run.py`
- `python scripts/benchmark_contract_dry_run.py --include-track-c-pilot`
- `python scripts/validate_repo_contracts.py --mode validate`
- `python scripts/validate_repo_contracts.py --mode test`
- `python scripts/build_execution_queue.py --mode write`
- `python scripts/build_execution_queue.py --mode check`
- `python scripts/run_repo_validation.py --include-track-c-pilot`
- `python scripts/run_repo_validation.py --require-rust --include-track-c-pilot`

## Rollback strategy

Revert the Track `C` editorial-refresh metadata, doctrine sections, validator checks, and governance/export changes as one unit if the editorial-only boundary cannot stay synchronized with the retained sample-sync and re-decision contracts.

## Evidence required for completion

- Track `C` editorial-only sample refresh allowances exist in shared metadata
- repo and benchmark validation fail when the editorial-only doctrine drifts
- the queue and decision register reflect the editorial-only boundary
- the next queue item remains a non-default Track `C` follow-on

## Completion evidence

- `scripts/benchmark_contract_metadata.py` now exports explicit editorial-only Track `C` sample refresh allowances, limited to JSON-equivalent formatting changes that preserve parsed sample content
- `BENCHMARK_STRATEGY.md` and `benchmarks/tracks.md` now mirror those editorial-only refresh allowances in machine-checkable list form, and `benchmarks/README.md` now states that editorial Track `C` sample refreshes are limited to JSON-equivalent formatting changes
- `scripts/benchmark_contract_dry_run.py` and `scripts/validate_repo_contracts.py` now fail if the Track `C` editorial-only refresh doctrine drifts
- `DR-020` records the editorial-only refresh boundary and the execution queue now advances to `Q-06-008`
