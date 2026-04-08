# 2026-04-08 Q-04-013 Harden Wasm Non-Emittable Contract Self-Tests

Status: complete
Owner: Codex
Date: 2026-04-08

## Objective

Add explicit repo-checker self-test coverage for the already-admitted helper-free Wasm non-emittable module contract so drift in published exclusion lists or exclusion markers fails fast under `scripts/validate_repo_contracts.py --mode test`.

## Scope

- add negative-fixture mutations for helper-free Wasm non-emittable Python and Rust module lists in `backends/wasm/README.md`
- add negative-fixture mutations for the supported-but-non-emittable Wasm module list and explicit exclusion marker in `LOWERING_CONTRACT.md`
- add a negative-fixture mutation for the supported-but-non-emittable helper-free Wasm module list in `VALIDATION_STRATEGY.md`
- keep queue and active-plan governance surfaces synchronized for one bounded Phase 4 hardening re-entry
- return the queue to `EMPTY BY DESIGN` once the self-test gap is closed

## Non-goals

- widen helper-free Wasm emission or change the admitted or non-emittable Wasm case sets
- change `WASM_BACKEND_METADATA`, pipeline emission behavior, or backend semantics
- reopen post-scalar ABI decisions, translation-validation promotion work, or benchmark scope
- change `SCIR-H` or `SCIR-L` semantics

## Touched files

- `plans/2026-04-08-q-04-013-harden-wasm-non-emittable-self-tests.md`
- `plans/2026-04-01-mvp-narrowing-and-contract-hardening.md`
- `EXECUTION_QUEUE.md`
- `scripts/validate_repo_contracts.py`
- `reports/exports/execution_queue.export.json`
- `reports/exports/checkpoint_closeout.export.json`

## Invariants that must remain true

- `SCIR-H` remains the only normative semantic representation
- `SCIR-L` remains derivative-only
- helper-free Wasm remains profile `P` with a `P2` ceiling
- the admitted and supported-but-non-emittable Wasm module sets remain unchanged
- this slice strengthens fail-fast coverage only and does not widen backend, reconstruction, or benchmark claims

## Risks

- mutation fixtures could fail for incidental parse or formatting reasons instead of the intended Wasm drift checks
- queue and export closeout artifacts could drift again if the governance surfaces are updated separately from the checker changes
- a hidden doctrine mismatch could surface during self-test expansion and require a bounded fix before closeout

## Validation steps

- `python scripts/validate_repo_contracts.py --mode test`
- `python scripts/validate_repo_contracts.py --mode validate`
- `python scripts/build_execution_queue.py --mode check`
- `python scripts/run_repo_validation.py --require-rust`

## Rollback strategy

Revert the self-test hardening patch set as one bounded slice if the new Wasm negative fixtures cannot be made to fail for the intended contract-drift reasons without changing the underlying Wasm doctrine.

## Evidence required for completion

- repo-checker self-tests cover helper-free Wasm non-emittable Python and Rust module-list drift
- repo-checker self-tests cover the supported-but-non-emittable module list and exclusion marker drift in `LOWERING_CONTRACT.md`
- repo-checker self-tests cover supported-but-non-emittable helper-free Wasm module-list drift in `VALIDATION_STRATEGY.md`
- queue and checkpoint exports match the final `Q-04-013` closeout state

## Completion evidence

- `scripts/validate_repo_contracts.py` now includes dedicated negative-fixture mutations for helper-free Wasm supported-but-non-emittable Python and Rust module lists in `backends/wasm/README.md`, the shared supported-but-non-emittable module list plus explicit backend-exclusion marker in `LOWERING_CONTRACT.md`, and the supported-but-non-emittable helper-free Wasm module list in `VALIDATION_STRATEGY.md`.
- The repo-checker self-test registry now executes those Wasm non-emittable drift fixtures and asserts the existing drift messages instead of leaving those headings covered only by normal validation.
- `EXECUTION_QUEUE.md` records `Q-04-013` as complete and returns the queue to `EMPTY BY DESIGN`; regenerated queue and checkpoint exports match that final state.
- Passed `python scripts/validate_repo_contracts.py --mode test`
- Passed `python scripts/validate_repo_contracts.py --mode validate`
- Passed `python scripts/build_execution_queue.py --mode check`
- Passed `python scripts/run_repo_validation.py --require-rust`

## CLOSEOUT

- Scope completed: the missing self-test coverage for helper-free Wasm supported-but-non-emittable contract drift is now explicit and fail-fast without changing the underlying backend contract.
- Invariants satisfied: admitted and excluded Wasm module sets stayed unchanged, helper-free Wasm remained bounded to the existing scalar and fixed record-cell slices, and no new backend or benchmark claim surface was activated.
- Residual risks: future Wasm contract headings still require synchronized mutation coverage whenever new list or marker checks are added; this slice does not widen any Wasm surface.
