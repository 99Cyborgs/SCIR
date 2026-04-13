# Bounded while-break-continue proof-loop promotion

Status: complete
Owner: Codex
Date: 2026-04-11

## Objective

Promote `b_while_break_continue` from importer-only canonical `SCIR-H` evidence into the bounded executable Python proof loop without widening grammar, helper-free Wasm, or the frozen Tier `A` sweep micro corpus.

## Scope

- move `b_while_break_continue` into the active executable Python proof loop and benchmark case set
- add exact-shape lowering, translation, reconstruction, and validation support for the current break/continue while-loop shape only
- synchronize Track `C` sample artifacts, benchmark/report contracts, and active focus/backlog records to the new 8-case executable corpus

## Non-goals

- widening grammar or normative `SCIR-H` / `SCIR-L` semantics
- promoting class cases or `d_try_except`
- widening helper-free Wasm beyond the existing bounded subset
- widening the frozen Tier `A` sweep micro corpus

## Touched files

- plans/2026-04-11-bounded-while-break-continue-promotion.md
- CURRENT_FOCUS.md
- BACKLOG.md
- frontend/python/IMPORT_SCOPE.md
- docs/feature_tiering.md
- docs/reconstruction_policy.md
- BENCHMARK_STRATEGY.md
- benchmarks/corpora_policy.md
- benchmarks/tracks.md
- benchmarks/success_failure_gates.md
- DECISION_REGISTER.md
- scripts/scir_python_bootstrap.py
- scripts/python_importer_conformance.py
- scripts/scir_bootstrap_pipeline.py
- scripts/benchmark_contract_metadata.py
- scripts/validate_repo_contracts.py
- tests/corpora/python_proof_loop_corpus.json
- schemas/benchmark_report.schema.json
- reports/examples/benchmark_report.example.json
- reports/examples/benchmark_track_c_manifest.example.json
- reports/examples/benchmark_track_c_result.example.json
- tests/python_importer/cases/b_while_break_continue/module_manifest.json
- tests/python_importer/cases/b_while_break_continue/feature_tier_report.json
- tests/python_importer/cases/b_while_break_continue/validation_report.json

## Invariants that must remain true

- `SCIR-H` remains the only normative semantic authority.
- `SCIR-L` stays derivative-only and does not gain new free-standing semantics.
- `b_while_break_continue` remains exact-shape only: `while x < 0`, nested `if x == -1: break`, `x = step(x)`, `continue`, then `return x`.
- helper-free Wasm stays unchanged; `b_while_break_continue` remains non-emittable.
- class cases and `d_try_except` remain importer-only.
- Track `C` remains non-default and keeps `c_opaque_call` boundary-accounting-only.

## Risks

- loop lowering can accidentally widen into generalized break/continue control instead of the admitted single shape
- reconstruction support can accidentally imply generic nested loop-control support
- benchmark and Track `C` sample counts can drift from the executable-case registry

## Validation steps

- python scripts/python_importer_conformance.py --mode validate-fixtures
- python scripts/sync_python_proof_loop_artifacts.py --mode write
- python scripts/sync_python_proof_loop_artifacts.py --mode check
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

If the break/continue path requires grammar widening, generalized loop-control semantics, or helper-free Wasm expansion, revert `b_while_break_continue` to importer-only `Tier B` and keep benchmark / Track `C` surfaces locked to the prior 7-case executable set.

## Evidence required for completion

- `python scripts/python_importer_conformance.py --mode validate-fixtures` passed
- `python scripts/sync_python_proof_loop_artifacts.py --mode write` and `--mode check` passed
- `python scripts/scir_bootstrap_pipeline.py --mode test` passed with compile/test evidence for 8 supported bootstrap cases
- `python scripts/benchmark_contract_dry_run.py` and `--include-track-c-pilot` passed; retained Track `C` stayed `mixed` with `repair_task_count = 8`, `accepted_case_count = 7`, and `boundary_only_case_count = 1`
- `python scripts/validate_repo_contracts.py --mode test` and `--mode audit` passed
- `python scripts/run_repo_validation.py` and `python scripts/run_repo_validation.py --require-rust --include-track-c-pilot` passed
- `make benchmark` and `make validate` passed
- regenerated checked-in Track `C` sample manifest/result and synchronized proof-loop corpus / benchmark surfaces keep class cases and `d_try_except` importer-only

## Completion evidence

- `python scripts/python_importer_conformance.py --mode validate-fixtures` passed.
- `python scripts/sync_python_proof_loop_artifacts.py --mode write` and `python scripts/sync_python_proof_loop_artifacts.py --mode check` passed and regenerated the checked-in `b_while_break_continue` fixture bundle plus retained Track `C` sample artifacts.
- `python scripts/scir_bootstrap_pipeline.py --mode test` passed and reported compile/test evidence for 8 supported bootstrap cases.
- `python scripts/benchmark_contract_dry_run.py` and `python scripts/benchmark_contract_dry_run.py --include-track-c-pilot` passed. Retained Track `C` stayed `mixed` with `repair_task_count = 8`, `accepted_case_count = 7`, and `boundary_only_case_count = 1`.
- `python scripts/validate_repo_contracts.py --mode test`, `--mode audit`, and `--mode validate` passed after the active-plan, benchmark-example, and Track `C` sample-posture checks were updated to the 8-case executable corpus.
- `python scripts/run_repo_validation.py` passed.
- `python scripts/run_repo_validation.py --require-rust --include-track-c-pilot` passed and kept the bounded Rust support lane green.
- `make benchmark` and `make validate` passed.
- Track `A` and `Track B` both passed on the widened executable corpus. The `K2` benchmark gate implementation was aligned to the documented compensating-gains rule by requiring `semantic_explicitness_gain <= 0` before a high source-ratio kill is triggered.
- Helper-free Wasm remained unchanged for this slice, and `b_class_init_method`, `b_class_field_update`, and `d_try_except` remained importer-only.
