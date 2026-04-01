# Phase 7 TypeScript Corpus Layout and Case Matrix

Status: complete
Owner: Codex
Date: 2026-03-30

## Objective

Define the initial TypeScript importer corpus layout and the first admitted/rejected case matrix that future importer work must satisfy, while keeping the slice importer-only and non-executable.

## Scope

- define the future `tests/typescript_importer/cases/` bundle layout
- define the first admitted interface-shaped witness cases and the first rejected boundary cases
- keep the corpus aligned with the existing importer fixture model and report bundle contract
- advance the execution queue to the next bounded importer-only Phase 7 task

## Non-goals

- creating actual TypeScript fixture files or directories
- implementing a TypeScript importer or conformance checker
- adding executable `D-JS`, lowering, reconstruction, or benchmark scope

## Touched files

- `plans/2026-03-30-phase7-typescript-corpus-layout-and-case-matrix.md`
- `plans/milestone_07_typescript_witness_slice.md`
- `frontend/typescript/IMPORT_SCOPE.md`
- `tests/README.md`
- `frontend/README.md`
- `EXECUTION_QUEUE.md`
- `reports/exports/execution_queue.export.json`

## Invariants that must remain true

- the first Phase 7 slice remains limited to interface declarations plus module-local witness consumption
- the future TypeScript corpus reuses the existing importer bundle model
- no TypeScript fixture in this slice implies executable downstream artifacts

## Risks

- case names could be too vague to guide future importer work
- the layout could diverge from Python/Rust fixture conventions and create unnecessary tool churn

## Validation steps

- `python scripts/build_execution_queue.py --mode check`
- `python scripts/validate_repo_contracts.py --mode validate`
- `python scripts/run_repo_validation.py`

## Rollback strategy

Revert the case-matrix and queue updates together if they leave the first TypeScript corpus ambiguous or imply broader semantic admission than the current witness doctrine allows.

## Evidence required for completion

- the future `tests/typescript_importer/cases/` layout is explicit
- the first admitted and rejected TypeScript cases are enumerated by stable case ID
- `Q-07-004` is complete and the next bounded Phase 7 item is explicit

## Completion evidence

- `plans/milestone_07_typescript_witness_slice.md` now defines the future `tests/typescript_importer/cases/` layout and the initial admitted/rejected case matrix
- `frontend/typescript/IMPORT_SCOPE.md`, `tests/README.md`, and `frontend/README.md` now agree on the stable first-slice TypeScript case IDs and bundle layout
- `EXECUTION_QUEUE.md` now marks `Q-07-004` complete and makes `Q-07-005` the next ready Phase 7 item
- `python scripts/build_execution_queue.py --mode check` passed on `2026-03-30`
- `python scripts/validate_repo_contracts.py --mode validate` passed on `2026-03-30`
- `python scripts/run_repo_validation.py` passed on `2026-03-30`
