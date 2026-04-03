# 2026-04-01 Q-06-005 Sync Track C Sample Evidence and Lock Criteria

Status: complete
Owner: Codex
Date: 2026-04-01

## Objective

Make the retained non-default Track `C` pilot's checked-in sample evidence an explicit synchronized contract with the opt-in runner output and the retained keep/retire criteria.

## Scope

- add explicit Track `C` sample-synchronization requirements to shared benchmark metadata
- mirror those requirements in machine-checkable benchmark doctrine sections
- make benchmark and repo validation fail if the sample-sync doctrine or checked-in sample evidence drifts
- add negative self-tests for Track `C` sample-sync drift
- record the governance decision and advance the queue to the next non-default Track `C` follow-on

## Non-goals

- no change to the default benchmark gate
- no broader repair corpus
- no new Track `C` schema or runner surface
- no weakening of Track `C` retirement triggers

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

- sample-sync doctrine can drift from the actual opt-in runner output if the requirements stay implicit
- validation can overfit to frozen sample values instead of enforcing synchronization plus retained criteria
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

Revert the Track `C` sample-sync metadata, doctrine sections, validator checks, and governance/export changes as one unit if the retained pilot's checked-in evidence cannot stay synchronized with the opt-in runner output.

## Evidence required for completion

- Track `C` sample-synchronization requirements exist in shared metadata
- repo and benchmark validation fail when the sample-sync doctrine or checked-in sample evidence drifts
- the queue and decision register reflect the locked sample-sync contract
- the next queue item remains a non-default Track `C` follow-on

## Completion evidence

- `scripts/benchmark_contract_metadata.py` now exports explicit Track `C` sample-synchronization requirements alongside the retained keep/retire contract
- `BENCHMARK_STRATEGY.md` and `benchmarks/tracks.md` now mirror those sample-synchronization requirements in machine-checkable list form, and `benchmarks/README.md` now states the sample bundle must stay identical to the opt-in pilot output while still satisfying the retained lock criteria
- `scripts/benchmark_contract_dry_run.py` and `scripts/validate_repo_contracts.py` now fail if the Track `C` sample-sync doctrine drifts, if the checked-in sample evidence drifts, or if the sample lock metrics weaken
- `DR-018` records the synchronized sample-bundle decision and the execution queue now advances to `Q-06-006`
