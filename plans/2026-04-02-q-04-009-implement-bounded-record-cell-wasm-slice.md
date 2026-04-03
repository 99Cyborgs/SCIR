# Q-04-009 Implement the bounded record-cell Wasm slice for `a_struct_field_borrow_mut`

Status: complete
Owner: Codex
Date: 2026-04-02

## Objective

Implement the smallest executable post-scalar Wasm slice: the existing Rust `a_struct_field_borrow_mut` case under the candidate record-cell ABI, without adding new `SCIR-L` semantics or broadening into general host/runtime contracts.

## Scope

- Make `a_struct_field_borrow_mut` Wasm-emittable under a bounded module-owned memory record-cell ABI.
- Extend the Wasm emitter, preservation reporting, and validation logic for that exact shape.
- Update Rust importer doctrine, Wasm backend doctrine, and repo-contract checks to match the widened active subset.
- Record the bounded implementation decision and advance the queue.

## Non-goals

- No broader record support beyond the fixed one-field `Counter.value: int` shape.
- No imported memory, allocator contract, host ABI, GC, dynamic layout, or polymorphic record support.
- No Python field-place Wasm emission.
- No async, opaque, imported, indirect, or recursive Wasm widening.

## Touched files

- scripts/scir_rust_bootstrap.py
- frontend/rust/IMPORT_SCOPE.md
- scripts/wasm_backend_metadata.py
- scripts/scir_bootstrap_pipeline.py
- backends/wasm/README.md
- LOWERING_CONTRACT.md
- VALIDATION_STRATEGY.md
- scripts/validate_repo_contracts.py
- DECISION_REGISTER.md
- EXECUTION_QUEUE.md
- reports/exports/decision_register.export.json
- reports/exports/execution_queue.export.json
- plans/2026-04-02-q-04-009-implement-bounded-record-cell-wasm-slice.md
- plans/2026-04-01-mvp-narrowing-and-contract-hardening.md

## Invariants that must remain true

- The bounded scalar helper-free subset remains supported unchanged.
- The new Wasm slice stays limited to `fixture.rust_importer.a_struct_field_borrow_mut` under the explicit record-cell ABI.
- No new `SCIR-L` ops are introduced.
- Wasm claims remain profile `P` with a `P2` ceiling and no native or host parity implication.

## Risks

- The implementation could accidentally imply a general record or host ABI instead of the fixed bounded case.
- Preservation reporting could omit candidate-specific downgrade reasons or evidence.
- Repo-contract validation could drift if Rust and Wasm doctrine are not widened together.

## Validation steps

- python -m py_compile scripts/scir_rust_bootstrap.py scripts/wasm_backend_metadata.py scripts/scir_bootstrap_pipeline.py scripts/validate_repo_contracts.py
- python scripts/scir_bootstrap_pipeline.py --mode validate
- python scripts/scir_bootstrap_pipeline.py --mode test
- python scripts/scir_bootstrap_pipeline.py --language rust --mode validate
- python scripts/scir_bootstrap_pipeline.py --language rust --mode test
- python scripts/validate_repo_contracts.py --mode validate
- python scripts/validate_repo_contracts.py --mode test
- python scripts/build_execution_queue.py --mode check
- python scripts/run_repo_validation.py
- python scripts/run_repo_validation.py --require-rust

## Rollback strategy

Revert the Wasm record-cell emission path, metadata widening, doctrine changes, and governance updates together if the slice cannot stay bounded to the fixed Rust field-mutation case.

## Evidence required for completion

- `a_struct_field_borrow_mut` emits stable bounded Wasm under the record-cell ABI.
- The preservation report includes the candidate-specific downgrade reasons and evidence.
- Rust importer doctrine and Wasm backend doctrine agree on the widened Wasm-emittable set.
- `Q-04-009` is closed, exports are synchronized, and validation passes.
