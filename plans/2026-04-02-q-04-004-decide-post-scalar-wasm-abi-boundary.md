# Q-04-004 Decide whether any broader Wasm backend work requires an explicit post-scalar ABI contract

Status: complete
Owner: Codex
Date: 2026-04-02

## Objective

Turn the field-place Wasm blocker into an explicit architecture and sequencing rule: broader Wasm work beyond the current helper-free scalar subset must not proceed incrementally without a deliberate backend ABI/storage contract decision.

## Scope

- Update root architecture and phase-order doctrine so the helper-free Wasm backend is explicitly scalar-only unless a broader ABI contract is adopted.
- Record a decision-register entry that future non-scalar Wasm widening requires an explicit ABI/storage contract.
- Add an open question for the post-scalar Wasm ABI decision point.
- Close `Q-04-004`, queue the next Wasm ABI decision slice, and synchronize exports.

## Non-goals

- No new Wasm ABI, memory model, host ABI, or record layout contract.
- No admission of `field.addr`, async, opaque, imported, indirect, or recursive Wasm cases.
- No change to Python or Rust executable proof-loop boundaries.
- No benchmark widening.

## Touched files

- ARCHITECTURE.md
- IMPLEMENTATION_PLAN.md
- OPEN_QUESTIONS.md
- DECISION_REGISTER.md
- EXECUTION_QUEUE.md
- reports/exports/open_questions.export.json
- reports/exports/decision_register.export.json
- reports/exports/execution_queue.export.json
- plans/2026-04-02-q-04-004-decide-post-scalar-wasm-abi-boundary.md
- plans/2026-04-01-mvp-narrowing-and-contract-hardening.md

## Invariants that must remain true

- The active helper-free Wasm backend remains limited to the current scalar subset under profile `P` with a `P2` ceiling.
- `H_FIELD_ADDR`, `H_AWAIT_RESUME`, and `H_OPAQUE_CALL` remain non-emittable.
- No broader Wasm memory or ABI contract is introduced implicitly through queue wording or architecture prose.
- Phase ordering remains Python proof loop -> Rust importer -> Wasm MVP -> benchmark loop.

## Risks

- The queue could keep generating incremental Wasm slices that implicitly assume a future ABI without recording the decision point.
- Architecture docs could still describe Wasm as an open-ended backend path instead of a bounded scalar subset.
- The new open question could drift from the decision-register constraint or queue wording.

## Validation steps

- python scripts/build_execution_queue.py --mode check
- python scripts/validate_repo_contracts.py --mode validate
- python scripts/validate_repo_contracts.py --mode test
- python scripts/run_repo_validation.py

## Rollback strategy

Revert the architecture, implementation-plan, decision-register, open-question, and queue updates together if they do not produce a clearer explicit decision point than the prior implicit continuation path.

## Evidence required for completion

- Root architecture and phase-order docs say the helper-free Wasm backend is scalar-only unless a broader ABI/storage contract is decided explicitly.
- The decision register records that broader Wasm widening now requires a deliberate backend ABI contract.
- `OPEN_QUESTIONS.md` contains the post-scalar Wasm ABI decision point.
- `Q-04-004` is closed, the next queue item points at that deliberate ABI decision, and the exports are synchronized.
