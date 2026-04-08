# 2026-04-08 Q-03-002 Rust Ownership-Mode Alignment

Status: complete
Owner: Codex
Date: 2026-04-08

## Objective

Make the admitted Rust ownership-bearing and unsafe-boundary cases use one explicit contract across importer scope, Rust bootstrap metadata, checked-in fixture bundles, and the optional Rust `H -> L` validation lane.

## Scope

- add an explicit Rust ownership/boundary contract for `a_struct_field_borrow_mut` and `c_unsafe_call`
- align `frontend/rust/IMPORT_SCOPE.md` with that contract
- align `scripts/scir_rust_bootstrap.py`, `scripts/rust_importer_conformance.py`, `scripts/scir_bootstrap_pipeline.py`, and `scripts/validate_repo_contracts.py` to the same contract
- regenerate the checked-in fixture bundles for `tests/rust_importer/cases/a_struct_field_borrow_mut/*` and `tests/rust_importer/cases/c_unsafe_call/*`
- keep the optional Rust `H -> L` validation lane importer-first and subset-bound

## Non-goals

- change `SCIR-H` or `SCIR-L` semantics
- activate Rust reconstruction, Rust benchmark claims, or broader backend claims
- add new Wasm-emittable Rust shapes
- widen unsupported Rust cases or alter the canonical ownership model

## Touched files

- `plans/2026-04-08-q-03-002-rust-ownership-mode-alignment.md`
- `plans/2026-04-01-mvp-narrowing-and-contract-hardening.md`
- `frontend/rust/IMPORT_SCOPE.md`
- `scir/contract_docs.py`
- `scripts/scir_rust_bootstrap.py`
- `scripts/rust_importer_conformance.py`
- `scripts/scir_bootstrap_pipeline.py`
- `scripts/validate_repo_contracts.py`
- `reports/exports/execution_queue.export.json`
- `reports/exports/checkpoint_closeout.export.json`
- `tests/rust_importer/cases/a_struct_field_borrow_mut/module_manifest.json`
- `tests/rust_importer/cases/a_struct_field_borrow_mut/feature_tier_report.json`
- `tests/rust_importer/cases/a_struct_field_borrow_mut/validation_report.json`
- `tests/rust_importer/cases/a_struct_field_borrow_mut/expected.scirh`
- `tests/rust_importer/cases/c_unsafe_call/module_manifest.json`
- `tests/rust_importer/cases/c_unsafe_call/feature_tier_report.json`
- `tests/rust_importer/cases/c_unsafe_call/validation_report.json`
- `tests/rust_importer/cases/c_unsafe_call/opaque_boundary_contract.json`

## Invariants that must remain true

- `SCIR-H` remains the only normative semantic representation
- `SCIR-L` remains derivative-only
- Rust remains importer-first evidence and does not become an active reconstruction, backend, or benchmark claim
- `borrow_mut<T>` remains the only writable borrow mode in the active subset
- explicit unsafe boundaries remain Tier `C`, capability-accounted, and preservation-bounded
- no new Wasm-emittable surface is admitted in this slice

## Risks

- ownership-mode wording could drift between importer scope prose, bootstrap metadata, and checked-in bundle artifacts
- the optional Rust `H -> L` validation lane could accidentally imply broader execution or profile claims if contract wording is sloppy
- changing Rust boundary metadata could desynchronize capability imports, boundary annotations, and downgrade expectations

## Validation steps

- `python scripts/rust_importer_conformance.py --mode validate-fixtures`
- `python scripts/scir_bootstrap_pipeline.py --language rust --mode validate`
- `python scripts/validate_repo_contracts.py --mode validate`
- `python scripts/run_repo_validation.py --require-rust`

## Rollback strategy

Revert the Rust importer alignment patch set as one unit if the ownership/boundary contract cannot be kept synchronized across docs, metadata, fixture bundles, and the optional Rust validation lane without widening active claims.

## Evidence required for completion

- `frontend/rust/IMPORT_SCOPE.md` and Rust bootstrap metadata publish the same explicit ownership/boundary contract for `a_struct_field_borrow_mut` and `c_unsafe_call`
- checked-in bundles for those two cases reflect the synchronized contract exactly
- repo validation fails if the Rust ownership/boundary contract drifts again
- all listed validation commands pass without widening Rust into reconstruction, benchmark, or broader backend claims

## Completion evidence

- `scir/contract_docs.py` now renders `frontend/rust/IMPORT_SCOPE.md` with an explicit ownership/boundary case list plus contract prose for `a_struct_field_borrow_mut` and `c_unsafe_call`, so the generated scope doc and `RUST_IMPORTER_METADATA` stay synchronized.
- `scripts/scir_rust_bootstrap.py` now publishes one Rust case contract for supported cases, including SCIR-H markers, required capabilities, translation expectations, and ownership/boundary membership; `c_unsafe_call` now uses active importer-first profile `R` instead of deferred profile `N`.
- `scripts/rust_importer_conformance.py`, `scripts/scir_bootstrap_pipeline.py`, and `scripts/validate_repo_contracts.py` now derive Rust SCIR-H markers, capability checks, translation-report expectations, and rendered-scope drift checks from the same metadata contract instead of parallel hard-coded maps.
- Regenerated `tests/rust_importer/cases/c_unsafe_call/*` now records the capability-accounted unsafe-boundary contract with `declared_profiles = ["R"]`; `a_struct_field_borrow_mut` regenerated cleanly without content change because the existing bundle already matched the explicit ownership-bearing contract.
- Passed `python scripts/rust_importer_conformance.py --mode validate-fixtures`
- Passed `python scripts/scir_bootstrap_pipeline.py --language rust --mode validate`
- Passed `python scripts/validate_repo_contracts.py --mode validate`
- Passed `python scripts/run_repo_validation.py --require-rust`

## CLOSEOUT

- Scope completed: the admitted Rust ownership-bearing and unsafe-boundary cases now use one explicit metadata contract across the generated import-scope doc, importer bundle validation, and optional Rust `H -> L` preservation reporting.
- Invariants satisfied: Rust remained importer-first, `borrow_mut<T>` remained explicit, the unsafe boundary stayed Tier `C` with capability accounting, and no new Wasm-emittable, reconstruction, or benchmark surface was activated.
- Residual risks: `EXECUTION_QUEUE.md` still records `Q-03-002` as the current ready item, so a separate governance closeout step is still needed before the queue itself reflects this slice as complete.
