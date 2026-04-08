# 2026-04-08 Q-03-003 Rust Async-Await Contract Alignment

Status: complete
Owner: Codex
Date: 2026-04-08

## Objective

Make the admitted Rust async/await case use one explicit contract across importer scope, Rust bootstrap metadata, repo drift checks, and the optional Rust `H -> L` validation lane.

## Scope

- add an explicit Rust await-bearing case list and contract for `a_async_await`
- align `frontend/rust/IMPORT_SCOPE.md` with that async contract through the generated contract-doc path
- align `scripts/scir_rust_bootstrap.py`, `scripts/scir_bootstrap_pipeline.py`, and `scripts/validate_repo_contracts.py` to the same await contract
- keep the admitted Rust async slice importer-first, non-Wasm-emittable, and subset-bound
- close the 2026-04-08 Rust re-entry pass back to an empty-by-design queue once the async contract slice is complete

## Non-goals

- change `SCIR-H` or `SCIR-L` semantics
- activate Rust reconstruction, Rust benchmark claims, or broader backend claims
- admit helper-free Wasm emission for async/await
- widen unsupported Rust cases or alter the canonical async model

## Touched files

- `plans/2026-04-08-q-03-003-rust-async-await-contract-alignment.md`
- `plans/2026-04-01-mvp-narrowing-and-contract-hardening.md`
- `EXECUTION_QUEUE.md`
- `scir/contract_docs.py`
- `frontend/rust/IMPORT_SCOPE.md`
- `scripts/scir_rust_bootstrap.py`
- `scripts/scir_bootstrap_pipeline.py`
- `scripts/validate_repo_contracts.py`
- `reports/exports/execution_queue.export.json`
- `reports/exports/checkpoint_closeout.export.json`

## Invariants that must remain true

- `SCIR-H` remains the only normative semantic representation
- `SCIR-L` remains derivative-only
- Rust remains importer-first evidence and does not become an active reconstruction, backend, or benchmark claim
- `a_async_await` remains non-Wasm-emittable in the helper-free backend subset
- explicit async/await semantics remain visible in canonical `SCIR-H` and the optional Rust `H -> L` validation lane
- no new Wasm-emittable surface is admitted in this slice

## Risks

- async/await wording could drift between importer scope prose, bootstrap metadata, and optional Rust validation expectations
- the optional Rust `H -> L` validation lane could accidentally imply backend support if the await contract is not explicit about non-emission
- queue, plan, and export artifacts could diverge again if the governance closeout is updated separately from the code-backed contract

## Validation steps

- `python scripts/build_execution_queue.py --mode check`
- `python scripts/rust_importer_conformance.py --mode validate-fixtures`
- `python scripts/scir_bootstrap_pipeline.py --language rust --mode validate`
- `python scripts/validate_repo_contracts.py --mode validate`
- `python scripts/run_repo_validation.py --require-rust`

## Rollback strategy

Revert the Rust async-contract alignment patch set as one unit if the await-bearing contract cannot be kept synchronized across docs, metadata, validation, and queue/governance artifacts without widening active claims.

## Evidence required for completion

- `frontend/rust/IMPORT_SCOPE.md` and Rust bootstrap metadata publish the same explicit await-bearing contract for `a_async_await`
- repo validation fails if the Rust async contract drifts again
- the optional Rust `H -> L` validation lane preserves the explicit await boundary without implying Wasm emission
- the queue reflects `Q-03-002` and `Q-03-003` as complete and returns to an empty-by-design posture with synchronized exports

## Completion evidence

- `scir/contract_docs.py` now renders `frontend/rust/IMPORT_SCOPE.md` with an explicit `Await-bearing cases` section plus an async contract paragraph for `a_async_await`, so the generated scope doc now publishes the admitted await-bearing Rust case directly instead of leaving it implicit inside the shape list.
- `scripts/scir_rust_bootstrap.py` now publishes one explicit `await_cases` contract list and validates that `a_async_await` remains a non-Wasm-emittable await-bearing case with an explicit `!await` marker and await-boundary preservation expectation.
- `scripts/scir_bootstrap_pipeline.py` now carries the await-case marker into Rust translation expectations and self-tests that the optional Rust `H -> L` validation lane keeps the await boundary explicit.
- `scripts/validate_repo_contracts.py` now fails if the generated Rust import-scope doc drifts on the await-bearing case list or loses the explicit async contract markers.
- `EXECUTION_QUEUE.md` now records `Q-03-002` and `Q-03-003` as complete and returns the queue to `EMPTY BY DESIGN`; regenerated queue and checkpoint exports now match that final state.
- Passed `python scripts/build_execution_queue.py --mode check`
- Passed `python scripts/rust_importer_conformance.py --mode validate-fixtures`
- Passed `python scripts/scir_bootstrap_pipeline.py --language rust --mode validate`
- Passed `python scripts/validate_repo_contracts.py --mode validate`
- Passed `python scripts/run_repo_validation.py --require-rust`

## CLOSEOUT

- Scope completed: the admitted Rust async/await case now has one explicit importer-first contract across generated scope docs, metadata validation, repo drift checks, and the optional Rust `H -> L` lane, and the Rust re-entry pass is closed back to a fail-closed queue posture.
- Invariants satisfied: Rust remained importer-first, `a_async_await` remained non-Wasm-emittable, the await boundary stayed explicit, and no new reconstruction, backend, or benchmark surface was activated.
- Residual risks: any further substantive work still requires a fresh roadmap-derived successor item and regenerated governance exports before the queue may leave `EMPTY BY DESIGN` again.
