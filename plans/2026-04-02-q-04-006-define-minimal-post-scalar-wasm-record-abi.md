# Q-04-006 Define the minimal post-scalar Wasm ABI/storage contract for record field mutation

Status: complete
Owner: Codex
Date: 2026-04-02

## Objective

Specify one minimal candidate post-scalar Wasm ABI/storage contract that could preserve the existing record field mutation semantics, without turning that design work into an execution claim yet.

## Scope

- Define a single candidate Wasm ABI/storage contract for fixed record field mutation.
- Record the contract in backend doctrine, architecture/governance, and validation strategy.
- Replace the broad contract-definition open question with the next narrower question about whether to operationalize the candidate contract.
- Advance the queue to the next Wasm slice focused on validator/report obligations for that candidate contract.

## Non-goals

- No implementation of the candidate ABI/storage contract.
- No admission of `field.addr` or record-carrying Wasm emission yet.
- No imported memory, host ABI, GC/object model, or broad runtime contract.
- No widening of async, opaque, imported, indirect, or recursive Wasm execution.

## Touched files

- ARCHITECTURE.md
- backends/wasm/README.md
- LOWERING_CONTRACT.md
- VALIDATION_STRATEGY.md
- OPEN_QUESTIONS.md
- DECISION_REGISTER.md
- EXECUTION_QUEUE.md
- reports/exports/open_questions.export.json
- reports/exports/decision_register.export.json
- reports/exports/execution_queue.export.json
- plans/2026-04-02-q-04-006-define-minimal-post-scalar-wasm-record-abi.md
- plans/2026-04-01-mvp-narrowing-and-contract-hardening.md

## Invariants that must remain true

- The active helper-free scalar Wasm backend remains the only executable Wasm surface.
- `H_FIELD_ADDR`, `H_AWAIT_RESUME`, and `H_OPAQUE_CALL` remain non-emittable until later implementation work adopts the contract.
- The candidate contract remains narrower than general object layout, host ABI, or imported-memory support.
- Wasm claims remain profile `P` and do not imply native or host parity.

## Risks

- The candidate contract could accidentally read as active support rather than design-track doctrine.
- The candidate could be too broad and silently reintroduce host/runtime semantics.
- Queue wording could drift from the exact candidate contract and reopen the same design question repeatedly.

## Validation steps

- python scripts/build_execution_queue.py --mode check
- python scripts/validate_repo_contracts.py --mode validate
- python scripts/validate_repo_contracts.py --mode test
- python scripts/run_repo_validation.py

## Rollback strategy

Revert the candidate-contract wording, open-question rewrite, decision-register entry, and queue updates together if the design slice does not stay clearly non-executable and subset-bound.

## Evidence required for completion

- The repository names one minimal candidate post-scalar Wasm ABI/storage contract.
- Backend and validation docs state that the candidate is design-track only and not yet executable.
- The prior broad contract-definition question is replaced with a narrower operationalization question.
- `Q-04-006` is closed, the next queue slice targets validator/report implications for the candidate contract, and exports are synchronized.
