# 2026-04-01 Q-06-001 Lock a Conditional Track C Python-Repair Pilot Without Widening the Default Gate

Status: complete
Owner: Codex
Date: 2026-04-01

## Objective

Prepare the first Track `C` pilot as a conditional, illustrative-only Python single-function repair pilot over the fixed Python proof-loop corpus without widening the default executable benchmark gate.

## Scope

- extend shared benchmark metadata with a conditional Track `C` pilot contract
- expose machine-checkable Track `C` pilot doctrine across benchmark docs
- add illustrative Track `C` manifest and result examples under `reports/examples/`
- make repository and benchmark validation fail when Track `C` pilot doctrine or sample artifacts drift
- resolve `OQ-005`, record the pilot decision, and advance the execution queue to the next conditional Track `C` slice

## Non-goals

- no Track `C` runner
- no default-gate activation for Track `C`
- no repository-scale repair corpus
- no Track `D` reactivation

## Touched files

- `BENCHMARK_STRATEGY.md`
- `benchmarks/tracks.md`
- `benchmarks/baselines.md`
- `benchmarks/corpora_policy.md`
- `benchmarks/success_failure_gates.md`
- `benchmarks/README.md`
- `reports/README.md`
- `reports/examples/benchmark_track_c_manifest.example.json`
- `reports/examples/benchmark_track_c_result.example.json`
- `scripts/benchmark_contract_metadata.py`
- `scripts/benchmark_contract_dry_run.py`
- `scripts/validate_repo_contracts.py`
- `DECISION_REGISTER.md`
- `OPEN_QUESTIONS.md`
- `EXECUTION_QUEUE.md`
- `reports/exports/decision_register.export.json`
- `reports/exports/open_questions.export.json`
- `reports/exports/execution_queue.export.json`
- `plans/2026-04-01-mvp-narrowing-and-contract-hardening.md`

## Invariants that must remain true

- Track `A` and Track `B` remain the only active executable benchmark gates
- Track `C` remains conditional and illustrative only
- the Track `C` pilot corpus remains the fixed executable Python proof-loop cases
- the Track `C` pilot uses direct source, typed-AST, and regularized-core baselines
- Track `C` sample artifacts stay outside the default executable benchmark bundle

## Risks

- the pilot doctrine can drift across docs, samples, and validators if the contract is duplicated
- example artifacts can accidentally be interpreted as executable benchmark output if the default-gate boundary is not checked explicitly
- governance updates can drift if markdown sources and derived exports are not kept synchronized

## Validation steps

- `python scripts/benchmark_contract_dry_run.py`
- `python scripts/validate_repo_contracts.py --mode validate`
- `python scripts/validate_repo_contracts.py --mode test`
- `python scripts/build_execution_queue.py --mode check`
- `python scripts/run_repo_validation.py`
- `python scripts/run_repo_validation.py --require-rust`

## Rollback strategy

Revert the Track `C` metadata, doctrine, sample artifacts, validator checks, and governance/export updates as one unit if the pilot cannot remain conditional and non-default under repository validation.

## Evidence required for completion

- one authoritative conditional Track `C` pilot contract exists in shared benchmark metadata
- repository and benchmark validation fail on Track `C` doctrine or sample-artifact drift
- `OQ-005` is resolved through a decision-register entry
- `Q-06-001` is closed, the next ready queue item remains a conditional Track `C` slice, and exports are synchronized

## Completion evidence

- `scripts/benchmark_contract_metadata.py` now defines the first Track `C` pilot as Python single-function repair over the fixed executable Python proof-loop cases with direct source, typed-AST, and regularized-core baselines plus `S2` and `K1` gates
- the benchmark doctrine docs now expose machine-checkable Track `C` pilot task-family, corpus, baseline, and gate sections
- `reports/examples/benchmark_track_c_manifest.example.json` and `reports/examples/benchmark_track_c_result.example.json` now provide illustrative-only Track `C` sample artifacts with `mixed` result posture
- `scripts/benchmark_contract_dry_run.py` and `scripts/validate_repo_contracts.py` now fail on Track `C` task-family, baseline, gate, or default-gate-boundary drift
- `DR-014` records the Track `C` pilot decision, `OQ-005` is removed, and the execution queue now advances to `Q-06-002`
