# Q-04-003 Assess whether field-place Wasm emission can stay helper-free without hidden layout semantics

Status: complete
Owner: Codex
Date: 2026-04-02

## Objective

Determine whether the smallest field-place lowering slice can be admitted into the helper-free Wasm backend without inventing hidden record layout, caller-visible mutation ABI, or host/runtime semantics.

## Scope

- Evaluate the existing Rust `a_struct_field_borrow_mut` lowering as the smallest concrete `field.addr` candidate.
- Make the helper-free Wasm blocker explicit in backend metadata, emitter errors, and backend doctrine if admission is not credible.
- Tighten repo-contract validation so the backend docs must keep the field-place blocker and explicit record ABI/layout absence visible.
- Record the blocker decision and advance the execution queue to the next deliberate Wasm-contract decision point.

## Non-goals

- No admission of `field.addr` into helper-free Wasm emission.
- No new record ABI, linear-memory convention, import surface, runtime shim, or host-runtime contract.
- No widening of async, opaque, imported, indirect, or recursive backend support.
- No Rust reconstruction or Rust benchmark activation.

## Touched files

- backends/wasm/README.md
- LOWERING_CONTRACT.md
- VALIDATION_STRATEGY.md
- scripts/wasm_backend_metadata.py
- scripts/scir_bootstrap_pipeline.py
- scripts/validate_repo_contracts.py
- DECISION_REGISTER.md
- EXECUTION_QUEUE.md
- reports/exports/decision_register.export.json
- reports/exports/execution_queue.export.json
- plans/2026-04-01-mvp-narrowing-and-contract-hardening.md

## Invariants that must remain true

- The helper-free Wasm backend remains profile `P` with a `P2` ceiling.
- `H_FIELD_ADDR`, `H_AWAIT_RESUME`, and `H_OPAQUE_CALL` remain non-emittable in the active Wasm subset.
- No helper imports, runtime shims, hidden record layout, or implicit host ABI assumptions are introduced.
- The only admitted helper-free Wasm modules remain `fixture.python_importer.a_basic_function`, `fixture.python_importer.b_direct_call`, and `fixture.rust_importer.a_mut_local`.

## Risks

- The backend could accidentally erase caller-visible borrowed-field mutation semantics by pretending a record field is just a scalar local.
- Docs could continue implying that `field.addr` is blocked only because of missing implementation detail rather than missing contract.
- Queue advancement could drift if the blocker decision and exports are not regenerated together.

## Validation steps

- python scripts/build_execution_queue.py --mode check
- python scripts/validate_repo_contracts.py --mode validate
- python scripts/validate_repo_contracts.py --mode test
- python scripts/scir_bootstrap_pipeline.py --mode validate
- python scripts/scir_bootstrap_pipeline.py --mode test
- python scripts/run_repo_validation.py

## Rollback strategy

Revert the blocker-specific metadata, emitter error path, doctrine updates, and queue/decision changes together if they do not produce a clearer fail-fast contract than the prior implicit rejection path.

## Evidence required for completion

- The helper-free Wasm backend rejects field-place lowering with an explicit record ABI/layout blocker instead of an incidental scalar-signature failure.
- The backend docs and validation strategy state that caller-visible borrowed-field mutation remains blocked without a deliberate backend-contract expansion.
- Repository validation fails if the field-place blocker wording drifts from the authoritative Wasm metadata.
- `Q-04-003` is closed, the next Wasm-contract decision point is queued, and the exports are synchronized.
