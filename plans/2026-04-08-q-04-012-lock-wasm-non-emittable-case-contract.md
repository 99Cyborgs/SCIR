# 2026-04-08 Q-04-012 Lock Wasm Non-Emittable Case Contract

Status: complete
Owner: Codex
Date: 2026-04-08

## Objective

Make the supported-but-non-emittable helper-free Wasm cases use one explicit contract across backend metadata, backend docs, validation doctrine, and pipeline validation.

## Scope

- publish explicit helper-free Wasm non-emittable case contracts for the supported Python and Rust async and boundary cases
- align `backends/wasm/README.md`, `LOWERING_CONTRACT.md`, and `VALIDATION_STRATEGY.md` to that backend exclusion contract
- align `scripts/wasm_backend_metadata.py`, `scripts/scir_bootstrap_pipeline.py`, and `scripts/validate_repo_contracts.py` to the same non-emittable case contract
- keep helper-free Wasm bounded to the already-admitted scalar and fixed record-cell slices
- close the queue back to `EMPTY BY DESIGN` once the bounded backend-contract slice is complete

## Non-goals

- widen helper-free Wasm emission to async, opaque, unsafe, imported, indirect, or broader direct-call shapes
- change `SCIR-H` or `SCIR-L` semantics
- reopen the frozen post-scalar Wasm ABI decision
- activate Rust reconstruction, Rust benchmarks, or broader backend claims

## Touched files

- `plans/2026-04-08-q-04-012-lock-wasm-non-emittable-case-contract.md`
- `plans/2026-04-01-mvp-narrowing-and-contract-hardening.md`
- `EXECUTION_QUEUE.md`
- `backends/wasm/README.md`
- `LOWERING_CONTRACT.md`
- `VALIDATION_STRATEGY.md`
- `scripts/wasm_backend_metadata.py`
- `scripts/scir_bootstrap_pipeline.py`
- `scripts/validate_repo_contracts.py`
- `reports/exports/execution_queue.export.json`
- `reports/exports/checkpoint_closeout.export.json`

## Invariants that must remain true

- `SCIR-H` remains the only normative semantic representation
- `SCIR-L` remains derivative-only
- helper-free Wasm remains profile `P` with a `P2` ceiling
- the only Wasm-emittable Python cases remain `a_basic_function` and `b_direct_call`
- the only Wasm-emittable Rust cases remain `a_mut_local` and `a_struct_field_borrow_mut`
- async and opaque or unsafe boundary cases remain explicit backend exclusions, not latent future support

## Risks

- backend docs could drift from the actual non-emittable module set if case-level exclusions remain duplicated manually
- generic non-emittable pipeline failures could hide which supported modules are supposed to remain excluded and why
- queue, plan, and export artifacts could diverge again if the backend-contract closeout is updated separately from the code-backed metadata

## Validation steps

- `python scripts/build_execution_queue.py --mode check`
- `python scripts/scir_bootstrap_pipeline.py --mode validate`
- `python scripts/scir_bootstrap_pipeline.py --language rust --mode validate`
- `python scripts/validate_repo_contracts.py --mode validate`
- `python scripts/run_repo_validation.py --require-rust`

## Rollback strategy

Revert the Wasm non-emittable-contract patch set as one unit if the supported-but-non-emittable case set cannot be kept synchronized across metadata, docs, validation, and queue/governance artifacts without widening active backend claims.

## Evidence required for completion

- backend metadata publishes the supported-but-non-emittable Python and Rust Wasm cases explicitly
- backend docs and validation doctrine publish the same supported-but-non-emittable module set
- pipeline validation fails if one of those supported-but-non-emittable cases emits helper-free Wasm or loses its declared blocking lowering rule
- the queue reflects `Q-04-012` as complete and returns to an empty-by-design posture with synchronized exports

## Completion evidence

- `scripts/wasm_backend_metadata.py` now publishes explicit supported-but-non-emittable helper-free Wasm contracts for `fixture.python_importer.a_async_await`, `fixture.python_importer.c_opaque_call`, `fixture.rust_importer.a_async_await`, and `fixture.rust_importer.c_unsafe_call`, each with module id, blocking lowering rule, exclusion kind, and reason.
- `scripts/scir_bootstrap_pipeline.py` now validates those non-emittable contracts directly: supported-but-non-emittable modules must keep their declared blocking lowering rules and must still fail Wasm emission, while output-set validation derives the blocked case lists from backend metadata instead of an ad hoc set difference.
- `backends/wasm/README.md`, `LOWERING_CONTRACT.md`, and `VALIDATION_STRATEGY.md` now publish the same supported-but-non-emittable module set explicitly, so async and opaque or unsafe backend exclusions are no longer only implied by lowering-rule prose.
- `scripts/validate_repo_contracts.py` now fails if the supported-but-non-emittable backend module lists or their required exclusion markers drift from `WASM_BACKEND_METADATA`.
- `EXECUTION_QUEUE.md` now records `Q-04-012` as complete and returns the queue to `EMPTY BY DESIGN`; regenerated queue and checkpoint exports now match that final state.
- Passed `python scripts/build_execution_queue.py --mode check`
- Passed `python scripts/scir_bootstrap_pipeline.py --mode validate`
- Passed `python scripts/scir_bootstrap_pipeline.py --language rust --mode validate`
- Passed `python scripts/validate_repo_contracts.py --mode validate`
- Passed `python scripts/run_repo_validation.py --require-rust`

## CLOSEOUT

- Scope completed: supported-but-non-emittable helper-free Wasm cases now use one explicit backend exclusion contract across metadata, docs, validation doctrine, and pipeline checks, without reopening any backend widening decision.
- Invariants satisfied: helper-free Wasm remained bounded to the existing scalar and fixed record-cell slices, async and opaque or unsafe cases remained explicit exclusions, and no new backend, reconstruction, or benchmark surface was activated.
- Residual risks: any further Wasm widening still requires a deliberate recorded contract decision; this slice only hardens the frozen exclusion boundary.
