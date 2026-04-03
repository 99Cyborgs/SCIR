# 2026-04-01 Q-03-001 Lock Rust Importer Evidence to the Canonical `SCIR-H` Kernel

Status: complete
Owner: Codex
Date: 2026-04-01

## Objective

Keep the Rust importer-first evidence path aligned to the locked canonical `SCIR-H` kernel without widening Rust into an active reconstruction, backend, or benchmark claim.

## Scope

- export one authoritative Rust importer-evidence metadata block from `scripts/scir_rust_bootstrap.py`
- derive Rust pipeline case classifications and translation expectations from that metadata
- align Rust importer conformance expectations to the same case contract
- add repository drift checks for machine-checkable Rust import-scope case lists
- close out `Q-03-001` and advance the execution queue to the next implementation phase

## Non-goals

- no Rust reconstruction activation
- no benchmark, schema, or profile-policy widening
- no new Rust grammar or source-shape admission
- no native or host-runtime parity claim changes

## Touched files

- `frontend/rust/IMPORT_SCOPE.md`
- `scripts/scir_rust_bootstrap.py`
- `scripts/rust_importer_conformance.py`
- `scripts/scir_bootstrap_pipeline.py`
- `scripts/validate_repo_contracts.py`
- `EXECUTION_QUEUE.md`
- `reports/exports/execution_queue.export.json`
- `plans/2026-04-01-mvp-narrowing-and-contract-hardening.md`

## Invariants that must remain true

- Rust remains importer-first evidence only in the MVP
- `SCIR-H` remains the only normative semantic layer
- `SCIR-L` remains derivative-only
- explicit unsafe boundaries remain visible and bounded
- Rust evidence does not become an active reconstruction or benchmark claim

## Risks

- stale Phase 6A-era Rust round-trip assumptions may still be embedded in dead code paths
- doc drift checks can become noisy if the Rust import-scope lists are not kept machine-checkable
- queue closeout can drift if the markdown and export are not regenerated together

## Validation steps

- `python scripts/validate_repo_contracts.py --mode validate`
- `python scripts/validate_repo_contracts.py --mode test`
- `python scripts/rust_importer_conformance.py --mode validate-fixtures`
- `python scripts/scir_bootstrap_pipeline.py --language rust --mode validate`
- `python scripts/scir_bootstrap_pipeline.py --language rust --mode test`
- `python scripts/build_execution_queue.py --mode check`
- `python scripts/run_repo_validation.py --require-rust`

## Rollback strategy

Revert the Rust metadata export, pipeline/conformance derivation, Rust drift checks, and queue/export updates as one unit if the importer-first Rust evidence contract cannot stay coherent under validation.

## Evidence required for completion

- `scripts/scir_rust_bootstrap.py` exports one authoritative Rust importer-evidence contract
- Rust pipeline and conformance case classifications derive from that contract
- repository validation fails on drift between the Rust metadata and `frontend/rust/IMPORT_SCOPE.md`
- `Q-03-001` is closed, the queue export is synchronized, and the Rust-required validation path passes

## Completion evidence

- `scripts/scir_rust_bootstrap.py` now exports `RUST_IMPORTER_METADATA` for the fixed Rust importer-first evidence corpus
- `scripts/scir_bootstrap_pipeline.py` now derives Rust supported, Tier `A`, rejected, translation, and Wasm-emittable case lists from that metadata and no longer carries stale Rust reconstruction-only helpers in the active code path
- `scripts/rust_importer_conformance.py` now derives Rust case expectations from `RUST_IMPORTER_METADATA` plus `CASE_CONFIG`
- `frontend/rust/IMPORT_SCOPE.md` now exposes machine-checkable lists for supported Rust cases, Tier `A` cases, the helper-free Wasm-admitted case, and rejected cases
- repository contract validation now fails on drift between `RUST_IMPORTER_METADATA` and `frontend/rust/IMPORT_SCOPE.md`
- `Q-03-001` is marked done in `EXECUTION_QUEUE.md` and the queue now advances to `Q-04-001`
- passed `python scripts/validate_repo_contracts.py --mode validate`
- passed `python scripts/validate_repo_contracts.py --mode test`
- passed `python scripts/rust_importer_conformance.py --mode validate-fixtures`
- passed `python scripts/scir_bootstrap_pipeline.py --language rust --mode validate`
- passed `python scripts/scir_bootstrap_pipeline.py --language rust --mode test`
- passed `python scripts/build_execution_queue.py --mode check`
- passed `python scripts/run_repo_validation.py --require-rust`
