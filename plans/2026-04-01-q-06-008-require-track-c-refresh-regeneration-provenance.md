# 2026-04-01 Q-06-008 Require Track C Refresh Regeneration Provenance

Status: complete
Owner: Codex
Date: 2026-04-01

## Objective

Make any non-editorial Track `C` sample refresh cite explicit regeneration provenance from the existing opt-in runner so checked-in sample updates cannot look hand-edited or untraceable.

## Scope

- add explicit non-editorial Track `C` sample-refresh provenance requirements to shared benchmark metadata
- mirror those provenance requirements in machine-checkable benchmark doctrine sections
- make benchmark and repo validation fail if the provenance doctrine drifts or if the operator-facing provenance rule disappears
- add negative self-tests for Track `C` sample-refresh provenance doctrine drift
- record the governance decision and advance the queue to the next bounded follow-on

## Non-goals

- no change to benchmark schemas or sample JSON shape
- no change to the default benchmark gate
- no new Track `C` runner behavior
- no weakening of the retained pilot's synchronization, re-decision, or editorial-only boundaries

## Touched files

- `BENCHMARK_STRATEGY.md`
- `benchmarks/README.md`
- `benchmarks/tracks.md`
- `reports/README.md`
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
- Track `C` editorial-only sample refreshes remain limited to JSON-equivalent formatting changes
- non-editorial Track `C` sample refreshes remain governance-bounded and traceable to the opt-in runner

## Risks

- provenance rules can become hand-wavy unless they cite exact runner fields and commands
- provenance doctrine can conflict with the existing sample-sync rules if it implies optional rather than required regeneration
- queue and decision exports can drift if not updated with the markdown sources

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

Revert the Track `C` provenance metadata, doctrine sections, validator checks, and governance/export changes as one unit if the provenance rule cannot stay narrow and synchronized with the retained sample bundle contract.

## Evidence required for completion

- Track `C` non-editorial sample-refresh provenance requirements exist in shared metadata
- repo and benchmark validation fail when the provenance doctrine drifts or the operator-facing provenance rule disappears
- the decision register and execution queue record the new provenance boundary
- the next queue item remains a bounded non-default Track `C` follow-on

## Completion evidence

- `scripts/benchmark_contract_metadata.py` now exports explicit non-editorial Track `C` sample-refresh provenance requirements tied to the opt-in benchmark command, opt-in validation command, regenerated manifest corpus hash, and regenerated result identifiers
- `BENCHMARK_STRATEGY.md` and `benchmarks/tracks.md` now mirror those provenance requirements in machine-checkable list form, and `benchmarks/README.md` plus `reports/README.md` now state the operator-facing provenance rule explicitly
- `scripts/benchmark_contract_dry_run.py` and `scripts/validate_repo_contracts.py` now fail if the Track `C` provenance doctrine drifts or if the operator-facing provenance rule disappears from the benchmark or reports readmes
- `DR-021` records the regeneration-provenance boundary and the execution queue now advances to `Q-06-009`
