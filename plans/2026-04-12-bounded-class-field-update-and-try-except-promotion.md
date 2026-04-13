# Bounded class-field-update and try/except promotion

Status: complete
Owner: Codex
Date: 2026-04-12

## Objective

Promote `b_class_field_update` into the executable Python proof loop and attempt a spec-first bounded activation of `d_try_except` only if the exact shape can be expressed coherently in canonical `SCIR-H`, derivative `SCIR-L`, reconstruction, and benchmark doctrine without widening helper-free Wasm or broader exception semantics.

## Scope

- promote `b_class_field_update` from importer-only `Tier B` to executable `Tier A`
- create one active plan and active focus item for the combined last-two-case Python slice
- update proof-loop, benchmark, Track `C`, and contract surfaces to the widened executable case set
- activate `d_try_except` only if a minimal exact-shape `SCIR-L` exception form is sufficient for lowering, validation, reconstruction, and benchmark evidence
- keep helper-free Wasm unchanged and non-emittable for both follow-on cases

## Non-goals

- generalized object semantics
- generalized exception lowering or standalone `throw`
- helper-free Wasm widening
- sweep-smoke widening
- Track `C` promotion into the default gate

## Touched files

- CURRENT_FOCUS.md
- BACKLOG.md
- DECISION_REGISTER.md
- docs/feature_tiering.md
- docs/reconstruction_policy.md
- docs/unsupported_cases.md
- frontend/python/IMPORT_SCOPE.md
- BENCHMARK_STRATEGY.md
- benchmarks/corpora_policy.md
- benchmarks/tracks.md
- benchmarks/success_failure_gates.md
- specs/scir_h_spec.md
- specs/scir_l_spec.md
- specs/type_effect_capability_model.md
- specs/validator_invariants.md
- LOWERING_CONTRACT.md
- scripts/scir_python_bootstrap.py
- scripts/python_importer_conformance.py
- scripts/scir_bootstrap_pipeline.py
- scripts/benchmark_contract_metadata.py
- scripts/benchmark_contract_dry_run.py
- scripts/sync_python_proof_loop_artifacts.py
- scripts/validate_repo_contracts.py
- tests/corpora/python_proof_loop_corpus.json
- schemas/benchmark_report.schema.json
- reports/examples/benchmark_report.example.json
- reports/examples/benchmark_track_c_manifest.example.json
- reports/examples/benchmark_track_c_result.example.json

## Invariants that must remain true

- `SCIR-H` remains the only normative semantic authority
- `SCIR-L` remains derivative-only
- helper-free Wasm remains unchanged and non-emittable for the new Python class-update and try/except cases
- the Tier `A` micro sweep stays frozen
- `c_opaque_call` remains the only boundary-only executable proof-loop case

## Risks

- bounded `d_try_except` may require a broader exception model than the current proof loop can support honestly
- benchmark, Track `C`, and repo-contract surfaces may drift if case-set updates do not move in lockstep
- exception-lowering validator changes could accidentally widen beyond the exact admitted try/catch shape

## Validation steps

- python scripts/sync_python_proof_loop_artifacts.py --mode write
- python scripts/sync_python_proof_loop_artifacts.py --mode check
- python scripts/python_importer_conformance.py --mode validate-fixtures
- python scripts/scir_bootstrap_pipeline.py --mode test
- python scripts/benchmark_contract_dry_run.py
- python scripts/benchmark_contract_dry_run.py --include-track-c-pilot
- python scripts/validate_repo_contracts.py --mode test
- python scripts/validate_repo_contracts.py --mode audit
- python scripts/run_repo_validation.py
- python scripts/run_repo_validation.py --require-rust --include-track-c-pilot
- make benchmark
- make validate

## Rollback strategy

If `d_try_except` cannot be kept exact-shape and subset-bound, revert its executable-promotion edits, keep it importer-only, and preserve only the bounded `b_class_field_update` promotion plus the plan evidence explaining the blocker.

## Evidence required for completion

- diff review showing exact executable-case registry, doctrine, and benchmark synchronization
- successful sequential validation for the required commands
- updated decision register entry or entries covering any new bounded executable exception claim
- plan status updated with the final completion evidence and any bounded rollback note if `d_try_except` remains importer-only

## Completion evidence

- `b_class_field_update` and `d_try_except` now appear in `scripts/scir_python_bootstrap.py` executable-case metadata and `tests/corpora/python_proof_loop_corpus.json`, widening the active proof loop and benchmark corpus to 11 executable Python cases with no importer-only canonical Python cases remaining.
- `scripts/scir_bootstrap_pipeline.py` now contains exact-shape executable support for both slices:
  - bounded record-like field update lowering, reconstruction, and execution for `b_class_field_update`
  - bounded single-handler `invoke`/`catch` lowering, reconstruction, and execution for `d_try_except`
- `SCIR-L` exception activation remained subset-bound:
  - `specs/scir_l_spec.md` admits only the exact `invoke`-based single-handler `ValueError` slice
  - helper-free Wasm remained unchanged and non-emittable for both new cases
- Benchmark/report and Track `C` contract surfaces were synchronized:
  - `schemas/benchmark_report.schema.json`
  - `reports/examples/benchmark_report.example.json`
  - `reports/examples/benchmark_track_c_manifest.example.json`
  - `reports/examples/benchmark_track_c_result.example.json`
  - `scripts/benchmark_contract_metadata.py`
  - `scripts/validate_repo_contracts.py`
- Sequential validation completed successfully on 2026-04-12:
  - `python scripts/sync_python_proof_loop_artifacts.py --mode write`
  - `python scripts/sync_python_proof_loop_artifacts.py --mode check`
  - `python scripts/python_importer_conformance.py --mode validate-fixtures`
  - `python scripts/scir_bootstrap_pipeline.py --mode test`
  - `python scripts/benchmark_contract_dry_run.py`
  - `python scripts/benchmark_contract_dry_run.py --include-track-c-pilot`
  - `python scripts/validate_repo_contracts.py --mode test`
  - `python scripts/validate_repo_contracts.py --mode audit`
  - `python scripts/validate_repo_contracts.py --mode validate`
  - `python scripts/run_repo_validation.py`
  - `python scripts/run_repo_validation.py --require-rust --include-track-c-pilot`
  - `make benchmark`
  - `make validate`
- Observed validation outcomes:
  - bootstrap pipeline: compile/test evidence for 11 supported bootstrap cases
  - Track A: `pass` with median SCIR/source ratio `1.5`
  - Track B: `pass` with Tier A compile/test `1.0`
  - retained Track C: `mixed` with `repair_task_count = 11`, `accepted_case_count = 10`, `boundary_only_case_count = 1`, `repair_accept_rate = 0.9091`, and typed-AST delta `0.875`
