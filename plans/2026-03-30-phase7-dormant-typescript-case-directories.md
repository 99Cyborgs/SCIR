# Phase 7 Dormant TypeScript Case Directories

Status: complete
Owner: Codex
Date: 2026-03-30

## Objective

Create the dormant on-disk TypeScript case directories for the fixed first-slice matrix without adding live fixture content or importer behavior.

## Scope

- create the placeholder-only case directories for all fixed admitted and rejected first-slice TypeScript IDs
- record the placeholder-on-disk state in the milestone and queue surfaces
- keep the corpus importer-only and non-executable

## Non-goals

- adding real fixture files
- implementing TypeScript importer behavior
- widening executable `D-JS`, lowering, reconstruction, or benchmark scope

## Touched files

- `plans/2026-03-30-phase7-dormant-typescript-case-directories.md`
- `tests/typescript_importer/cases/*/README.md`
- `tests/README.md`
- `plans/milestone_07_typescript_witness_slice.md`
- `EXECUTION_QUEUE.md`
- `reports/exports/execution_queue.export.json`

## Invariants that must remain true

- the fixed TypeScript case matrix remains placeholder-only
- admitted and rejected bundle expectations remain unchanged
- no live TypeScript fixture content is introduced

## Risks

- placeholder directories could be mistaken for active fixtures if their purpose is not explicit
- directory naming drift would undercut the fixed case matrix already published in doctrine

## Validation steps

- `python scripts/build_execution_queue.py --mode check`
- `python scripts/validate_repo_contracts.py --mode validate`
- `python scripts/run_repo_validation.py`

## Rollback strategy

Remove the placeholder directories and related queue/docs updates together if the on-disk scaffold implies active fixtures or importer execution.

## Evidence required for completion

- every fixed first-slice TypeScript case has a corresponding placeholder directory on disk
- the milestone and queue record that the dormant case matrix now exists physically
- `Q-07-007` is complete and the next bounded Phase 7 item is explicit

## Completion evidence

- every fixed TypeScript case ID now has a corresponding placeholder directory under `tests/typescript_importer/cases/`
- each directory contains a local `README.md` that makes the placeholder-only status explicit and preserves the admitted/rejected bundle distinction
- `EXECUTION_QUEUE.md` now marks `Q-07-007` complete and makes `Q-07-008` the next ready Phase 7 item
- `python scripts/build_execution_queue.py --mode check` passed on `2026-03-30`
- `python scripts/validate_repo_contracts.py --mode validate` passed on `2026-03-30`
- `python scripts/run_repo_validation.py` passed on `2026-03-30`
