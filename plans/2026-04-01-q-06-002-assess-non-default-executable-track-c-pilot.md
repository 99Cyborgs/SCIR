# 2026-04-01 Q-06-002 Assess a Non-default Executable Track C Pilot Without Widening the Default Gate

Status: complete
Owner: Codex
Date: 2026-04-01

## Objective

Determine whether the first Track `C` Python single-function repair pilot is justified as an explicit opt-in executable slice while keeping Tracks `A` and `B` as the only default executable benchmark gates.

## Scope

- promote the conditional Track `C` pilot metadata from samples-only posture to an explicit opt-in executable pilot contract
- add the non-default Track `C` runner and wire it through the optional validation entrypoint only
- keep machine-checkable benchmark doctrine, sample artifacts, and repo-contract checks aligned to the opt-in pilot posture
- record the governance decision, close `Q-06-002`, and advance the queue to the next still-non-default Track `C` slice

## Non-goals

- no change to `make benchmark`
- no change to the default `python scripts/run_repo_validation.py` gate
- no broader repair corpus
- no Track `C` promotion into an active executable benchmark track

## Touched files

- `README.md`
- `VALIDATION.md`
- `VALIDATION_STRATEGY.md`
- `BENCHMARK_STRATEGY.md`
- `benchmarks/README.md`
- `benchmarks/tracks.md`
- `reports/README.md`
- `reports/examples/benchmark_track_c_manifest.example.json`
- `reports/examples/benchmark_track_c_result.example.json`
- `scripts/benchmark_contract_metadata.py`
- `scripts/benchmark_contract_dry_run.py`
- `scripts/run_repo_validation.py`
- `scripts/validate_repo_contracts.py`
- `DECISION_REGISTER.md`
- `EXECUTION_QUEUE.md`
- `reports/exports/decision_register.export.json`
- `reports/exports/execution_queue.export.json`
- `plans/2026-04-01-mvp-narrowing-and-contract-hardening.md`

## Invariants that must remain true

- Track `A` and Track `B` remain the only active executable benchmark gates
- the Track `C` executable pilot remains explicit opt-in only
- the Track `C` corpus remains the fixed executable Python proof-loop cases
- `c_opaque_call` remains boundary-accounting-only inside the Track `C` pilot
- the checked-in Track `C` sample artifacts remain outside the default executable benchmark gate

## Risks

- the optional Track `C` command could accidentally leak into `make benchmark` or the default validation runner
- sample artifacts can drift from the actual bounded pilot output if the metadata and runner stop matching
- governance and queue updates can drift if markdown and export regeneration are not updated together

## Validation steps

- `python scripts/benchmark_contract_dry_run.py`
- `python scripts/benchmark_contract_dry_run.py --include-track-c-pilot`
- `python scripts/validate_repo_contracts.py --mode validate`
- `python scripts/validate_repo_contracts.py --mode test`
- `python scripts/build_execution_queue.py --mode write`
- `python scripts/build_execution_queue.py --mode check`
- `python scripts/run_repo_validation.py`
- `python scripts/run_repo_validation.py --include-track-c-pilot`
- `python scripts/run_repo_validation.py --require-rust`

## Rollback strategy

Revert the Track `C` opt-in runner wiring, doctrine updates, sample-artifact refresh, and governance/export changes as one unit if the optional pilot cannot stay explicit, bounded, and outside the default gate.

## Evidence required for completion

- the Track `C` pilot is executable only through explicit opt-in commands
- repo and benchmark validation fail if the Track `C` opt-in pilot leaks into the default gate
- the checked-in Track `C` sample artifacts match the bounded opt-in pilot output
- `DR-015` records the non-default pilot decision, `Q-06-002` is closed, and the next queue item remains a conditional Track `C` slice

## Completion evidence

- `scripts/benchmark_contract_metadata.py` now fixes the Track `C` pilot as a non-default executable Python single-function repair slice with explicit executable versus boundary-only case sets
- `scripts/run_repo_validation.py` and `scripts/benchmark_contract_dry_run.py` now expose Track `C` only through `--include-track-c-pilot`, while `Makefile` and the default validation runner remain Track `A` / `B` only
- benchmark doctrine docs now expose machine-checkable Track `C` executable-pilot posture markers and explicit opt-in commands
- `reports/examples/benchmark_track_c_manifest.example.json` and `reports/examples/benchmark_track_c_result.example.json` now mirror the bounded opt-in pilot output instead of a looser illustrative placeholder
- `scripts/validate_repo_contracts.py` now fails when the Track `C` pilot leaks into `make benchmark` or the default validation runner
- `DR-015` records the non-default executable pilot decision and the execution queue now advances to `Q-06-003`
