# 2026-04-02 Q-02-002 Promote `b_direct_call` Into the Python Proof Loop

Status: complete
Owner: Codex
Date: 2026-04-02

## Objective

Promote the bounded `b_direct_call` Python fixture from importer-only evidence into the active executable proof loop, then tighten validator and completeness surfaces so the widened proof-loop contract fails fast if it drifts.

## Scope

- move `b_direct_call` into the authoritative executable Python proof-loop metadata
- implement `SCIR-H -> SCIR-L` lowering alignment for the fixed direct-call shape
- make the Python reconstruction and preservation path treat `b_direct_call` as an active supported case
- widen the active benchmark case set only as required by the executable proof-loop contract
- update validator, checklist, feature-tier, benchmark, decision, queue, and sample/export surfaces that must agree with the widened executable case set

## Non-goals

- no promotion of loops, `try/catch`, class-field shapes, or broader Tier `B` Python cases
- no Wasm promotion for direct-call cases
- no change to Rust executable scope
- no change to Track `D` or broad repository-scale repair doctrine

## Touched files

- `scripts/scir_python_bootstrap.py`
- `scripts/scir_bootstrap_pipeline.py`
- `scripts/benchmark_contract_metadata.py`
- `scripts/benchmark_contract_dry_run.py`
- `scripts/validate_repo_contracts.py`
- `frontend/python/IMPORT_SCOPE.md`
- `docs/reconstruction_policy.md`
- `SPEC_COMPLETENESS_CHECKLIST.md`
- `docs/feature_tiering.md`
- `BENCHMARK_STRATEGY.md`
- `benchmarks/*`
- `reports/examples/benchmark_track_c_manifest.example.json`
- `reports/examples/benchmark_track_c_result.example.json`
- `DECISION_REGISTER.md`
- `EXECUTION_QUEUE.md`
- `reports/exports/decision_register.export.json`
- `reports/exports/execution_queue.export.json`
- `plans/2026-04-01-mvp-narrowing-and-contract-hardening.md`

## Invariants that must remain true

- the Python proof loop remains the decisive end-to-end MVP path
- `b_direct_call` is the only Tier `B` Python case promoted by this slice
- loop, `break`, `continue`, class, and `try/catch` follow-on cases remain importer-only
- direct-call promotion does not imply helper-free Wasm emission
- `c_opaque_call` remains profile `D-PY`, preservation ceiling `P3`, and boundary-accounting-only

## Risks

- widening executable cases also widens benchmark and Track `C` sample surfaces, which can create contract drift if not updated together
- direct-call lowering could accidentally overclaim Wasm support if non-emittable rules are not kept explicit
- feature-tier and completeness docs can drift if they still describe all direct calls as already fully supported without naming the bounded executable shape

## Validation steps

- `python scripts/python_importer_conformance.py --mode validate-fixtures`
- `python scripts/scir_bootstrap_pipeline.py --mode validate`
- `python scripts/scir_bootstrap_pipeline.py --mode test`
- `python scripts/benchmark_contract_dry_run.py`
- `python scripts/benchmark_contract_dry_run.py --include-track-c-pilot`
- `python scripts/validate_repo_contracts.py --mode validate`
- `python scripts/validate_repo_contracts.py --mode test`
- `python scripts/build_execution_queue.py --mode write`
- `python scripts/build_execution_queue.py --mode check`
- `python scripts/run_repo_validation.py`
- `python scripts/run_repo_validation.py --include-track-c-pilot`
- `python scripts/run_repo_validation.py --require-rust --include-track-c-pilot`

## Rollback strategy

Revert the direct-call proof-loop promotion, benchmark widening, validator/checklist updates, and governance/export changes as one unit if the bounded direct-call shape cannot stay aligned across importer, lowering, reconstruction, and benchmark doctrine.

## Evidence required for completion

- `b_direct_call` is an executable Python proof-loop case in shared metadata and the pipeline
- repo and benchmark validation fail if the widened executable Python case set drifts
- the direct-call case remains non-emittable for helper-free Wasm
- decision and queue surfaces record the proof-loop widening and the new next action

## Completion evidence

- `scripts/scir_python_bootstrap.py` now classifies `b_direct_call` as an executable Tier `A` Python proof-loop case and keeps it in the benchmark case set while leaving Wasm emission disabled
- `scripts/scir_bootstrap_pipeline.py` now lowers, validates, reconstructs, and benchmark-executes the fixed `b_direct_call` shape while keeping loops, classes, and `try/catch` importer-only
- `scripts/python_importer_conformance.py`, `frontend/python/IMPORT_SCOPE.md`, and `docs/reconstruction_policy.md` now agree that `b_direct_call` is active end to end
- benchmark doctrine and checked-in Track `C` sample artifacts now reflect the widened four-case proof-loop corpus and the corresponding three accepted non-opaque repair cases
- `DR-022` records the bounded proof-loop widening, `Q-02-002` is closed, and the queue now points to validator/completeness hardening before any further Wasm widening
