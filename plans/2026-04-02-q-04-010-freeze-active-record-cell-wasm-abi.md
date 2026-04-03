# Q-04-010 Freeze the active Wasm record-cell ABI at the fixed Rust slice

Status: complete
Owner: Codex
Date: 2026-04-02

## Objective

Record an explicit freeze decision that keeps the active Wasm record-cell ABI limited to the fixed Rust `a_struct_field_borrow_mut` slice rather than widening into broader record layouts or Python field-place support.

## Scope

- Update architecture and Wasm backend doctrine to state that the active record-cell ABI is frozen to the fixed Rust slice.
- Resolve the current Wasm-widening open question in favor of the freeze decision.
- Record the decision, advance the queue, and synchronize derived exports.

## Non-goals

- No additional Wasm implementation widening.
- No Python field-place Wasm activation.
- No broader record ABI, imported-memory, host ABI, or parity claims.
- No benchmark or Track `C` changes.

## Touched files

- ARCHITECTURE.md
- backends/wasm/README.md
- LOWERING_CONTRACT.md
- VALIDATION_STRATEGY.md
- OPEN_QUESTIONS.md
- DECISION_REGISTER.md
- EXECUTION_QUEUE.md
- reports/exports/decision_register.export.json
- reports/exports/open_questions.export.json
- reports/exports/execution_queue.export.json
- plans/2026-04-02-q-04-010-freeze-active-record-cell-wasm-abi.md
- plans/2026-04-01-mvp-narrowing-and-contract-hardening.md

## Invariants that must remain true

- The scalar helper-free Wasm subset remains supported unchanged.
- The only active post-scalar Wasm slice remains `fixture.rust_importer.a_struct_field_borrow_mut`.
- Broader record layouts, Python field-place Wasm, imported memory, and host ABI claims remain out of scope.
- Wasm preservation claims remain profile `P` with explicit `P2` ceilings where record-cell downgrades apply.

## Risks

- The freeze decision could be documented inconsistently across architecture and backend doctrine.
- Queue state could still imply future silent widening if the next boundary is not explicit.

## Validation steps

- python scripts/build_execution_queue.py --mode write
- python scripts/build_execution_queue.py --mode check
- python scripts/validate_repo_contracts.py --mode validate
- python scripts/validate_repo_contracts.py --mode test
- python scripts/run_repo_validation.py
- python scripts/run_repo_validation.py --require-rust

## Rollback strategy

Revert the freeze-decision doctrine, decision-register entry, queue update, and regenerated exports together if the repository cannot keep the active Wasm boundary explicit and synchronized.

## Evidence required for completion

- The active Wasm record-cell ABI is explicitly frozen to the fixed Rust slice in architecture and backend doctrine.
- `OQ-009` is resolved and the queue no longer implies incremental widening of the record-cell ABI.
- Derived exports are synchronized and validation passes.
