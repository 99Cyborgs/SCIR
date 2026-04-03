# Q-04-005 Open a deliberate post-scalar Wasm ABI/storage design track

Status: complete
Owner: Codex
Date: 2026-04-02

## Objective

Record that SCIR will actively design, rather than indefinitely defer, a post-scalar Wasm ABI/storage contract for records and caller-visible mutation, while keeping the current helper-free scalar backend unchanged until that contract is specified explicitly.

## Scope

- Resolve the prior blocker question about whether to open broader Wasm ABI/storage design work.
- Record a decision-register entry opening the post-scalar Wasm ABI/storage design track.
- Replace the old broad open question with a narrower contract-definition question.
- Advance the execution queue from the blocked “whether” decision to the first explicit contract-definition slice.

## Non-goals

- No new record ABI/storage contract yet.
- No admission of `field.addr`, async, opaque, imported, indirect, recursive, or host-facing Wasm execution.
- No change to the active helper-free scalar Wasm backend.
- No benchmark or frontend widening.

## Touched files

- ARCHITECTURE.md
- IMPLEMENTATION_PLAN.md
- OPEN_QUESTIONS.md
- DECISION_REGISTER.md
- EXECUTION_QUEUE.md
- reports/exports/open_questions.export.json
- reports/exports/decision_register.export.json
- reports/exports/execution_queue.export.json
- plans/2026-04-02-q-04-005-open-post-scalar-wasm-abi-design-track.md
- plans/2026-04-01-mvp-narrowing-and-contract-hardening.md

## Invariants that must remain true

- The active helper-free Wasm backend remains scalar-only under profile `P` with a `P2` ceiling.
- `H_FIELD_ADDR`, `H_AWAIT_RESUME`, and `H_OPAQUE_CALL` remain non-emittable until a broader contract is specified and adopted.
- Opening the design track does not imply runtime parity, native parity, or host parity.
- Any broader Wasm semantics still require explicit contract definition before implementation.

## Risks

- The repo could accidentally imply that opening the design track means post-scalar Wasm support is now active.
- The open question could remain too broad and fail to focus the next slice on a concrete contract shape.
- Queue wording could drift from the new decision register entry.

## Validation steps

- python scripts/build_execution_queue.py --mode check
- python scripts/validate_repo_contracts.py --mode validate
- python scripts/validate_repo_contracts.py --mode test
- python scripts/run_repo_validation.py

## Rollback strategy

Revert the architecture, plan, open-question, decision-register, and queue updates together if they do not clearly distinguish “active design track” from “active backend support.”

## Evidence required for completion

- The repository records that post-scalar Wasm ABI/storage design is now in scope.
- The active scalar Wasm backend remains explicitly unchanged.
- The old blocker question is replaced with a narrower contract-definition question.
- `Q-04-005` is closed, the next ready slice defines the minimal ABI/storage contract shape, and exports are synchronized.
