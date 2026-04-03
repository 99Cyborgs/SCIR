# 2026-04-01 Q-06-004 Lock Track C Retention and Retirement Criteria

Status: complete
Owner: Codex
Date: 2026-04-01

## Objective

Make the retained non-default Track `C` pilot’s keep and retire conditions explicit, machine-checkable, and synchronized across metadata, doctrine, and validation.

## Scope

- add explicit Track `C` retention criteria and retirement triggers to shared benchmark metadata
- expose those criteria in machine-checkable benchmark doctrine sections
- make benchmark and repo validation fail if the criteria drift
- record the governance decision and advance the queue to the next non-default Track `C` slice

## Non-goals

- no change to the default benchmark gate
- no broader repair corpus
- no schema change
- no new executable Track `C` surface beyond the existing opt-in pilot

## Touched files

- `BENCHMARK_STRATEGY.md`
- `benchmarks/README.md`
- `benchmarks/success_failure_gates.md`
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
- a failed Track `C` retention condition forces re-decision rather than silent retention

## Risks

- criteria can drift between metadata, docs, and code if duplicated inconsistently
- retirement triggers can become weaker than the actual pilot checks
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

Revert the Track `C` retention metadata, doctrine sections, validator checks, and governance/export changes as one unit if the retained pilot criteria cannot stay synchronized.

## Evidence required for completion

- Track `C` retention criteria and retirement triggers exist in shared metadata
- repo and benchmark validation fail when those criteria drift
- the queue and decision register reflect the locked retention/retirement contract
- the next queue item remains a non-default Track `C` follow-on

## Completion evidence

- `scripts/benchmark_contract_metadata.py` now exports explicit Track `C` retention criteria and retirement triggers
- `BENCHMARK_STRATEGY.md` and `benchmarks/success_failure_gates.md` now mirror those criteria in machine-checkable list form
- `scripts/benchmark_contract_dry_run.py` and `scripts/validate_repo_contracts.py` now fail if the Track `C` retention or retirement contract drifts
- `DR-017` records the retained pilot’s lock conditions and the execution queue now advances to `Q-06-005`
