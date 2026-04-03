# 2026-04-01 Q-06-006 Require Track C Sample Posture Re-Decision

Status: complete
Owner: Codex
Date: 2026-04-01

## Objective

Make it explicit and machine-checkable that changing the retained non-default Track `C` sample bundle's posture requires a new decision-register entry and queue update before the checked-in sample bundle may change.

## Scope

- add explicit Track `C` sample-posture re-decision triggers to shared benchmark metadata
- mirror those triggers in machine-checkable benchmark doctrine sections
- make benchmark and repo validation fail with governance-specific messages when the checked-in Track `C` sample posture drifts
- add negative self-tests for Track `C` sample-posture re-decision drift
- record the governance decision and advance the queue to the next non-default Track `C` follow-on

## Non-goals

- no change to the default benchmark gate
- no broader repair corpus
- no new Track `C` runner or schema
- no weakening of the retained pilot's keep/retire criteria

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

- posture-changing sample edits can still look like ordinary sample refreshes unless the governance boundary is stated explicitly
- validation can keep failing generically on sample drift instead of making the required re-decision path obvious
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

Revert the Track `C` sample-posture governance metadata, doctrine sections, validator messaging, and governance/export changes as one unit if the re-decision boundary cannot stay synchronized with the retained pilot contract.

## Evidence required for completion

- Track `C` sample-posture re-decision triggers exist in shared metadata
- repo and benchmark validation fail with governance-specific messages when the checked-in Track `C` sample posture drifts
- the queue and decision register reflect the new re-decision boundary
- the next queue item remains a non-default Track `C` follow-on

## Completion evidence

- `scripts/benchmark_contract_metadata.py` now exports explicit Track `C` sample-posture re-decision triggers alongside the retained sample-sync contract
- `BENCHMARK_STRATEGY.md` and `benchmarks/tracks.md` now mirror those re-decision triggers in machine-checkable list form, and `benchmarks/README.md` now states that posture-changing sample refreshes require a new decision-register entry and queue update
- `scripts/benchmark_contract_dry_run.py` and `scripts/validate_repo_contracts.py` now fail with governance-specific Track `C` re-decision messages when the checked-in sample status, evidence, or case/boundary posture drifts
- `DR-019` records the sample-posture re-decision boundary and the execution queue now advances to `Q-06-007`
