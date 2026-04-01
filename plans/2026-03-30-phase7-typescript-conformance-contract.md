# Phase 7 TypeScript Conformance Contract

Status: complete
Owner: Codex
Date: 2026-03-30

## Objective

Define the future TypeScript importer conformance-checker contract and the repository-validation entrypoint expectations for the importer-only interface-witness corpus.

## Scope

- define the future TypeScript conformance-checker role, mode contract, and corpus assumptions
- define the pre-checker and post-checker repository-validation posture for the Phase 7 TypeScript corpus
- update queue and milestone surfaces so the contract is explicit before any TypeScript importer code exists

## Non-goals

- implementing importer code or a live TypeScript conformance checker
- creating TypeScript fixture bundles or directories in this slice
- adding executable `D-JS`, lowering, reconstruction, or benchmark scope

## Touched files

- `plans/2026-03-30-phase7-typescript-conformance-contract.md`
- `plans/milestone_07_typescript_witness_slice.md`
- `VALIDATION_STRATEGY.md`
- `tests/README.md`
- `frontend/README.md`
- `EXECUTION_QUEUE.md`
- `reports/exports/execution_queue.export.json`

## Invariants that must remain true

- the first Phase 7 slice remains importer-only and non-executable
- the future TypeScript checker must reuse the Python/Rust conformance pattern
- current validation must not imply that the TypeScript checker already exists

## Risks

- future-entrypoint wording could be misread as a currently available command
- validation doctrine could accidentally require TypeScript importer execution before the checker exists

## Validation steps

- `python scripts/build_execution_queue.py --mode check`
- `python scripts/validate_repo_contracts.py --mode validate`
- `python scripts/run_repo_validation.py`

## Rollback strategy

Revert the future-checker contract and queue updates together if the new wording implies implemented TypeScript checker behavior or executable witness validation that does not exist.

## Evidence required for completion

- the future TypeScript conformance-checker contract is explicit
- repository-validation expectations are explicit for both the pre-checker and post-checker states
- `Q-07-005` is complete and the next bounded Phase 7 item is explicit

## Completion evidence

- `plans/milestone_07_typescript_witness_slice.md` now defines the future TypeScript checker role, expected modes, and pre-checker validation posture
- `VALIDATION_STRATEGY.md`, `tests/README.md`, and `frontend/README.md` now agree on the future conformance-checker contract and on the fact that it is not yet implemented
- `EXECUTION_QUEUE.md` now marks `Q-07-005` complete and makes `Q-07-006` the next ready Phase 7 item
- `python scripts/build_execution_queue.py --mode check` passed on `2026-03-30`
- `python scripts/validate_repo_contracts.py --mode validate` passed on `2026-03-30`
- `python scripts/run_repo_validation.py` passed on `2026-03-30`
