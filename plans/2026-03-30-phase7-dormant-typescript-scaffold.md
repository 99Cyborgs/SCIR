# Phase 7 Dormant TypeScript Scaffold

Status: complete
Owner: Codex
Date: 2026-03-30

## Objective

Reserve the dormant TypeScript conformance scaffold and corpus root on disk without adding importer logic or executable witness behavior.

## Scope

- create the reserved `tests/typescript_importer/` tree with explanatory placeholders
- add the reserved `scripts/typescript_importer_conformance.py` entrypoint
- update docs and queue state to reflect the reserved-but-inactive scaffold

## Non-goals

- implementing TypeScript importer logic
- creating live fixture bundles
- adding executable `D-JS`, lowering, reconstruction, or benchmark behavior

## Touched files

- `plans/2026-03-30-phase7-dormant-typescript-scaffold.md`
- `tests/typescript_importer/README.md`
- `tests/typescript_importer/cases/README.md`
- `scripts/typescript_importer_conformance.py`
- `VALIDATION_STRATEGY.md`
- `tests/README.md`
- `frontend/README.md`
- `plans/milestone_07_typescript_witness_slice.md`
- `EXECUTION_QUEUE.md`
- `reports/exports/execution_queue.export.json`

## Invariants that must remain true

- the scaffold remains dormant and importer-only
- the placeholder script fails clearly instead of pretending to validate anything
- no TypeScript executable path is introduced

## Risks

- a placeholder script could be mistaken for a working checker if the failure mode is vague
- the reserved tree could look like an active corpus if the placeholder docs are unclear

## Validation steps

- `python scripts/build_execution_queue.py --mode check`
- `python scripts/validate_repo_contracts.py --mode validate`
- `python scripts/run_repo_validation.py`
- `python scripts/typescript_importer_conformance.py --help`
- `python scripts/typescript_importer_conformance.py --mode validate-fixtures`

## Rollback strategy

Remove the dormant script and reserved tree together if the scaffold implies a live TypeScript checker or executable path.

## Evidence required for completion

- the dormant TypeScript corpus root exists on disk with explicit placeholder docs
- the reserved conformance entrypoint exists and fails clearly as not implemented
- `Q-07-006` is complete and the next bounded Phase 7 item is explicit

## Completion evidence

- `tests/typescript_importer/README.md` and `tests/typescript_importer/cases/README.md` now reserve the on-disk TypeScript corpus root and bundle expectations
- `scripts/typescript_importer_conformance.py` now exists as a dormant entrypoint with reserved `validate-fixtures` and `test` modes and a clear not-implemented failure path
- `EXECUTION_QUEUE.md` now marks `Q-07-006` complete and makes `Q-07-007` the next ready Phase 7 item
- `python scripts/build_execution_queue.py --mode check` passed on `2026-03-30`
- `python scripts/validate_repo_contracts.py --mode validate` passed on `2026-03-30`
- `python scripts/run_repo_validation.py` passed on `2026-03-30`
- `python scripts/typescript_importer_conformance.py --help` exposed the reserved future contract
- `python scripts/typescript_importer_conformance.py --mode validate-fixtures` failed explicitly as reserved/not implemented
