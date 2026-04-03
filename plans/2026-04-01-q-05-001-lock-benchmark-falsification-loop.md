# 2026-04-01 Q-05-001 Lock the Benchmark Falsification Loop to the Fixed Python Proof Loop

Status: complete
Owner: Codex
Date: 2026-04-01

## Objective

Keep the active benchmark falsification loop aligned to the fixed Python proof loop so Track `A` and Track `B` doctrine, executable manifests, and validation cannot drift without failing.

## Scope

- export one authoritative benchmark contract metadata module for the active executable tracks, benchmark cases, baselines, gates, profiles, and contamination controls
- derive Track `A` and Track `B` executable manifests plus gate expectations from that metadata instead of parallel hard-coded benchmark constants
- make benchmark doctrine docs expose machine-checkable active track, case, baseline, and gate lists
- add repository drift checks and dry-run self-tests for benchmark track, baseline, and gate drift
- close `Q-05-001` and advance the execution queue beyond the benchmark falsification loop handoff

## Non-goals

- no activation of Track `C` execution
- no reactivation of Track `D`
- no new benchmark schema fields
- no second-language benchmark claims

## Touched files

- `BENCHMARK_STRATEGY.md`
- `benchmarks/tracks.md`
- `benchmarks/baselines.md`
- `benchmarks/success_failure_gates.md`
- `scripts/benchmark_contract_metadata.py`
- `scripts/scir_bootstrap_pipeline.py`
- `scripts/benchmark_contract_dry_run.py`
- `scripts/validate_repo_contracts.py`
- `EXECUTION_QUEUE.md`
- `reports/exports/execution_queue.export.json`
- `plans/2026-04-01-mvp-narrowing-and-contract-hardening.md`

## Invariants that must remain true

- only Track `A` and Track `B` remain active executable benchmark tracks
- benchmark cases remain the fixed executable Python proof-loop cases only
- mandatory active baselines remain direct source and typed-AST
- Track `C` remains conditional and Track `D` remains deferred
- benchmark doctrine does not imply runtime, backend, or second-language benchmark activation

## Risks

- benchmark doctrine is currently duplicated across docs, dry-run validation, and executable manifest builders
- centralizing track metadata can accidentally widen executable benchmark artifacts if bundle validation is not tightened at the same time
- queue closeout can drift if the markdown and export are not regenerated together

## Validation steps

- `python scripts/benchmark_contract_dry_run.py`
- `python scripts/validate_repo_contracts.py --mode validate`
- `python scripts/validate_repo_contracts.py --mode test`
- `python scripts/build_execution_queue.py --mode check`
- `python scripts/run_repo_validation.py`
- `python scripts/run_repo_validation.py --require-rust`

## Rollback strategy

Revert the shared benchmark metadata module, benchmark doc list checks, executable manifest derivation, and queue/export updates as one unit if the fixed Python proof-loop benchmark contract cannot stay coherent under validation.

## Evidence required for completion

- one authoritative benchmark contract metadata module exists on disk
- Track `A` and Track `B` executable manifests derive from that metadata
- repository and benchmark dry-run validation fail on drift between benchmark metadata and doctrine docs
- `Q-05-001` is closed, the queue export is synchronized, and both default and Rust-required validation paths pass

## Completion evidence

- `scripts/benchmark_contract_metadata.py` now exports the authoritative benchmark contract for active executable tracks, benchmark cases, baselines, gates, profiles, and contamination controls
- `scripts/scir_bootstrap_pipeline.py` now derives Track `A` and Track `B` executable benchmark manifests from that metadata, including benchmark cases, baselines, profiles, gates, and Track `B` compile/test case selection
- `scripts/benchmark_contract_dry_run.py` now validates doctrine docs and executable benchmark bundles against that metadata and includes negative self-tests for benchmark case, baseline, and gate drift
- `scripts/validate_repo_contracts.py` now fails on drift between benchmark metadata and the machine-checkable benchmark doctrine sections in `BENCHMARK_STRATEGY.md`, `benchmarks/tracks.md`, `benchmarks/baselines.md`, and `benchmarks/success_failure_gates.md`
- `Q-05-001` is closed, `reports/exports/execution_queue.export.json` is synchronized, and the next ready slice is `Q-06-001`
