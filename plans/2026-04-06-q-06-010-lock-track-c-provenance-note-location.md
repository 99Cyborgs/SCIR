# 2026-04-06 Q-06-010 Lock Track C Provenance-Note Location

Status: complete
Owner: Codex
Date: 2026-04-06

## Objective

Lock one deterministic checked-in location for any non-editorial Track `C` sample-refresh provenance note so operators can discover the governing note without path guesswork.

## Scope

- add an authoritative Track `C` provenance-note storage path to shared benchmark metadata
- mirror that storage-location rule in benchmark doctrine and operator readmes
- generate and check a checked-in provenance note at the fixed path alongside the existing Track `C` sample manifest and result
- make benchmark and repository validation fail if the location doctrine drifts or if the checked-in note no longer matches the generator-backed Track `C` sample outputs
- record the governance decision and advance the queue to the next bounded Track `C` follow-on

## Non-goals

- no change to benchmark schemas
- no new Track `C` runner behavior
- no widening of the default benchmark gate
- no relaxation of the retained pilot’s synchronization, provenance, or re-decision boundaries

## Touched files

- `BENCHMARK_STRATEGY.md`
- `benchmarks/README.md`
- `benchmarks/tracks.md`
- `reports/README.md`
- `reports/examples/benchmark_track_c_refresh_provenance.example.md`
- `scripts/benchmark_contract_metadata.py`
- `scripts/benchmark_contract_dry_run.py`
- `scripts/sync_python_proof_loop_artifacts.py`
- `scripts/validate_repo_contracts.py`
- `DECISION_REGISTER.md`
- `EXECUTION_QUEUE.md`
- `reports/exports/decision_register.export.json`
- `reports/exports/execution_queue.export.json`
- `plans/2026-04-01-mvp-narrowing-and-contract-hardening.md`

## Invariants that must remain true

- Track `A` and Track `B` remain the only default executable benchmark gates
- Track `C` remains explicit opt-in only
- the provenance note remains sibling governance evidence for the retained sample bundle, not a new benchmark result artifact class
- the checked-in note remains generator-backed from the same Track `C` sample manifest and result contract

## Risks

- a location rule without generator-backed checking would still let the checked-in note drift from the sample JSON files
- adding a note file outside `reports/examples/` would weaken discoverability by splitting the retained sample bundle
- validator wording can drift if benchmark doctrine, reports readme, and sync script point at different paths

## Validation steps

- `python scripts/sync_python_proof_loop_artifacts.py --mode check`
- `python scripts/benchmark_contract_dry_run.py --include-track-c-pilot`
- `python scripts/validate_repo_contracts.py --mode validate`
- `python scripts/validate_repo_contracts.py --mode test`
- `python scripts/build_execution_queue.py --mode write`
- `python scripts/build_execution_queue.py --mode check`
- `python scripts/run_repo_validation.py --include-track-c-pilot`

## Rollback strategy

Revert the provenance-note path metadata, checked-in note, sync-script changes, doctrine updates, and governance/export updates as one slice if the fixed note location cannot stay synchronized with the retained Track `C` sample bundle.

## Evidence required for completion

- shared metadata exports one deterministic Track `C` provenance-note path
- the checked-in provenance note at that path is generator-backed from the current Track `C` sample outputs
- benchmark and repository validation fail if the path rule drifts or if the checked-in note content drifts
- the decision register and execution queue record the new storage-location boundary and next bounded follow-on

## Completion evidence

- `scripts/benchmark_contract_metadata.py` now exports the fixed Track `C` provenance-note path and a generator-backed renderer for the checked-in note content
- `scripts/sync_python_proof_loop_artifacts.py` now checks and writes `reports/examples/benchmark_track_c_refresh_provenance.example.md` alongside the Track `C` sample manifest and result
- `BENCHMARK_STRATEGY.md`, `benchmarks/tracks.md`, `benchmarks/README.md`, and `reports/README.md` now name the exact checked-in note path and keep it tied to the retained Track `C` sample bundle
- `scripts/benchmark_contract_dry_run.py` and `scripts/validate_repo_contracts.py` now fail if the Track `C` provenance-note storage rule drifts or if the checked-in note content no longer matches the generator-backed sample bundle
- `DR-038` records the deterministic storage-location boundary, `Q-06-010` is closed, and the execution queue now advances to `Q-06-011`
