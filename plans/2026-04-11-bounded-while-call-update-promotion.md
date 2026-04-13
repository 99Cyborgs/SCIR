# Bounded while-call-update proof-loop promotion

Status: complete
Owner: Codex
Date: 2026-04-11

## Objective

Promote `b_while_call_update` from importer-only canonical `SCIR-H` evidence into the bounded executable Python proof loop without widening grammar, helper-free Wasm, or the frozen Tier `A` sweep micro corpus.

## Scope

- move `b_while_call_update` into the active executable Python proof loop and benchmark case set
- add exact-shape lowering, translation, reconstruction, and validation support for the current while-loop shape only
- synchronize Track `C` sample artifacts, benchmark/report contracts, and active focus/backlog records to the new 7-case executable corpus

## Non-goals

- widening grammar or normative `SCIR-H` / `SCIR-L` semantics
- promoting `b_while_break_continue`, class cases, or `d_try_except`
- widening helper-free Wasm beyond the existing bounded subset
- widening the frozen Tier `A` sweep micro corpus

## Touched files

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

## Invariants that must remain true

- `SCIR-H` remains the only normative semantic authority.
- `SCIR-L` stays derivative-only and does not gain new free-standing semantics.
- `b_while_call_update` remains exact-shape only: `while x < 0: x = step(x)` followed by `return x`.
- helper-free Wasm stays unchanged; `b_while_call_update` remains non-emittable.
- `b_while_break_continue`, class cases, and `d_try_except` remain importer-only.
- Track `C` remains non-default and keeps `c_opaque_call` boundary-accounting-only.

## Risks

- loop lowering can accidentally widen into generalized loop control instead of the admitted single shape
- reconstruction support can accidentally imply generic `loop` / `break` support
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

If the while-loop path requires grammar widening, generalized loop semantics, or helper-free Wasm expansion, revert `b_while_call_update` to importer-only `Tier B` and keep benchmark / Track `C` surfaces locked to the prior 6-case executable set.

## Evidence required for completion

- `python scripts/python_importer_conformance.py --mode validate-fixtures` passed
- `python scripts/sync_python_proof_loop_artifacts.py --mode write` and `--mode check` passed
- `python scripts/scir_bootstrap_pipeline.py --mode test` passed with compile/test evidence for 7 supported bootstrap cases
- `python scripts/benchmark_contract_dry_run.py` and `--include-track-c-pilot` passed; retained Track `C` stayed `mixed` with `accepted_case_count = 6` and `boundary_only_case_count = 1`
- `python scripts/validate_repo_contracts.py --mode test` and `--mode audit` passed
- `python scripts/run_repo_validation.py` and `python scripts/run_repo_validation.py --require-rust --include-track-c-pilot` passed
- `make benchmark` and `make validate` passed
- regenerated checked-in Track `C` sample manifest/result and synchronized proof-loop corpus / benchmark surfaces keep `b_while_break_continue`, class cases, and `d_try_except` importer-only
