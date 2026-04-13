# Truth-Surface Cleanup and Bounded Proof-Loop Promotion

Status: in-progress
Owner: Codex
Date: 2026-04-11

## Objective

Remove false-maturity surfaces that contradict the active SCIR boundary, then promote the smallest credible Python follow-on case (`b_if_else_return`) into the executable proof loop without widening grammar or inventing new semantic lanes.

## Scope

- quarantine archived TypeScript placeholder fixtures so they no longer imply Tier `A` or active profile support
- remove dormant Track `D` executable helpers from the active bootstrap pipeline
- align validation docs and repository-contract checks to the actual default command surface
- promote `b_if_else_return` from importer-only Tier `B` canonical `SCIR-H` evidence to executable Tier `A` proof-loop coverage
- refresh benchmark, corpus, and retained Track `C` sample contracts that are mechanically tied to the executable proof-loop case set

## Non-goals

- grammar widening beyond the existing admitted Python shape
- reactivating TypeScript, Track `D`, or broad runtime claims
- promoting Rust, Wasm, or Track `C` to the active widening target
- changing `SCIR-H` / `SCIR-L` normative semantics outside the bounded case promotion

## Touched files

- `CURRENT_FOCUS.md`
- `BACKLOG.md`
- `DECISION_REGISTER.md`
- `BENCHMARK_STRATEGY.md`
- `VALIDATION_STRATEGY.md`
- `docs/feature_tiering.md`
- `frontend/python/IMPORT_SCOPE.md`
- `frontend/typescript/IMPORT_SCOPE.md`
- `tests/README.md`
- `ci/validation_pipeline.md`
- `benchmarks/README.md`
- `benchmarks/tracks.md`
- `benchmarks/success_failure_gates.md`
- `reports/README.md`
- `scripts/validate_repo_contracts.py`
- `scripts/typescript_importer_conformance.py`
- `scripts/scir_python_bootstrap.py`
- `scripts/scir_bootstrap_pipeline.py`
- `scripts/benchmark_contract_metadata.py`
- `scripts/benchmark_contract_dry_run.py`
- `scripts/python_importer_conformance.py`
- `scripts/wasm_backend_metadata.py`
- `tests/corpora/python_proof_loop_corpus.json`
- `tests/typescript_importer/cases/*`
- `reports/examples/benchmark_track_c_manifest.example.json`
- `reports/examples/benchmark_track_c_result.example.json`

## Invariants that must remain true

- `SCIR-H` remains the only normative semantic authority
- `SCIR-L` remains derivative-only and subset-bound
- deferred TypeScript surfaces remain outside the default validation and benchmark gate
- Track `D` remains deferred and absent from the active executable pipeline surface
- benchmark cases remain locked to executable Python proof-loop cases
- retained Track `C` remains non-default and diagnostic-only

## Risks

- widening one Python case also widens Track `A`, Track `B`, and the retained Track `C` pilot contracts through shared metadata
- corpus, benchmark, and sample-sync docs can drift if the executable case-set change is only partially propagated
- removing Track `D` residue from the pipeline could accidentally disturb unrelated validator-hardening edits if the block boundary is cut incorrectly

## Validation steps

- `python scripts/typescript_importer_conformance.py --mode validate-fixtures`
- `python scripts/validate_repo_contracts.py --mode test`
- `python scripts/validate_repo_contracts.py --mode audit`
- `python scripts/python_importer_conformance.py --mode validate-fixtures`
- `python scripts/scir_bootstrap_pipeline.py --mode test`
- `python scripts/benchmark_contract_dry_run.py --output-dir artifacts/benchmark_runs/latest`
- `python scripts/run_repo_validation.py`
- `python scripts/run_repo_validation.py --require-rust --include-track-c-pilot`

## Rollback strategy

Revert the proof-loop promotion if `b_if_else_return` requires new semantics, new profile claims, or benchmark exceptions. Keep the truth-surface cleanup even if the promotion is rolled back.

## Evidence required for completion

- clean diff showing the TypeScript archive lane no longer encodes Tier `A` / active-profile claims
- clean diff showing dormant Track `D` helpers removed from `scripts/scir_bootstrap_pipeline.py`
- refreshed corpus, benchmark, and Track `C` sample artifacts synchronized to the promoted executable case set
- passing default validation, audit validation, proof-loop test mode, and Rust-plus-Track-`C` validation
