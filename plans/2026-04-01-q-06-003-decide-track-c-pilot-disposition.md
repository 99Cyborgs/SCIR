# 2026-04-01 Q-06-003 Decide Track C Pilot Disposition Without Promoting It Into the Default Gate

Status: complete
Owner: Codex
Date: 2026-04-01

## Objective

Make an explicit keep, harden, or retire decision for the first non-default executable Track `C` pilot while preserving the bounded Python repair corpus and the default Track `A` / `B` gate.

## Scope

- encode the current Track `C` pilot disposition in shared benchmark metadata
- expose machine-checkable doctrine for that disposition in benchmark docs
- make benchmark and repo validation fail if the retained non-default posture drifts
- update checked-in Track `C` sample evidence to reflect the retained bounded-diagnostic decision
- record the decision, close `Q-06-003`, and advance the queue to a follow-on retention-criteria slice

## Non-goals

- no promotion of Track `C` into an active executable benchmark track
- no broadening beyond the fixed Python repair cases
- no new benchmark schema
- no change to `make benchmark` or the default validation runner

## Touched files

- `BENCHMARK_STRATEGY.md`
- `benchmarks/README.md`
- `benchmarks/tracks.md`
- `reports/README.md`
- `reports/examples/benchmark_track_c_result.example.json`
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
- the Track `C` corpus remains the fixed executable Python proof-loop cases
- `c_opaque_call` remains boundary-accounting-only inside the pilot
- the Track `C` sample result remains bounded and must not overclaim promotion readiness

## Risks

- a retained-disposition rule could silently diverge between metadata, docs, and sample output
- the optional pilot could start passing validation while no longer justifying retention
- queue and decision exports can drift if markdown and generated exports are not updated together

## Validation steps

- `python scripts/benchmark_contract_dry_run.py`
- `python scripts/benchmark_contract_dry_run.py --include-track-c-pilot`
- `python scripts/validate_repo_contracts.py --mode validate`
- `python scripts/validate_repo_contracts.py --mode test`
- `python scripts/build_execution_queue.py --mode write`
- `python scripts/build_execution_queue.py --mode check`
- `python scripts/run_repo_validation.py --include-track-c-pilot`

## Rollback strategy

Revert the Track `C` disposition metadata, doctrine, sample-result evidence, and governance/export updates as one unit if the retained posture cannot be enforced consistently.

## Evidence required for completion

- the Track `C` pilot has an explicit retained, hardened, or retired disposition in benchmark metadata
- repo and benchmark validation fail when that disposition drifts
- the checked-in Track `C` sample result reflects the chosen disposition
- `DR-016` records the choice, `Q-06-003` is closed, and the next queue item remains non-default Track `C` work

## Completion evidence

- `scripts/benchmark_contract_metadata.py` now records the Track `C` pilot disposition as a retained bounded diagnostic pilot with explicit accepted-case and status expectations
- `scripts/benchmark_contract_dry_run.py` and `scripts/validate_repo_contracts.py` now fail if the retained Track `C` posture, accepted-case count, or `K1`/`S2` status drifts
- benchmark doctrine docs now expose machine-checkable Track `C` disposition sections rather than leaving the keep-or-retire choice implicit
- `reports/examples/benchmark_track_c_result.example.json` now includes retained-diagnostic evidence rather than implying a promotion claim
- `DR-016` records the retained disposition and the execution queue now advances to `Q-06-004`
