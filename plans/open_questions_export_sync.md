# Open Questions Export Sync

Status: complete
Owner: Codex
Date: 2026-03-15

## Objective

Create a checked-in machine-readable export for `OPEN_QUESTIONS.md` and make repository validation prove the markdown, schema, and export remain synchronized.

## Scope

- add a schema for the open-questions register
- add a checked-in derived export under `reports/exports/`
- extend the repository checker to parse `OPEN_QUESTIONS.md`, validate the export, and fail on drift
- update validation-facing docs to describe the new derived export

## Non-goals

- resolving any open question
- changing SCIR semantics, benchmark doctrine, or assumptions
- adding a generic export system for unrelated markdown files

## Touched files

- `plans/open_questions_export_sync.md`
- `schemas/open_questions.schema.json`
- `reports/README.md`
- `reports/exports/open_questions.export.json`
- `scripts/validate_repo_contracts.py`
- `README.md`
- `VALIDATION_STRATEGY.md`
- `ci/validation_pipeline.md`
- `docs/repository_map.md`

## Invariants that must remain true

- `OPEN_QUESTIONS.md` remains the normative human-readable source
- the checked-in export is derived rather than independently authored
- no unresolved question is silently reinterpreted during export
- `make validate` remains the blocking top-level validation command

## Risks

- schema design could add fields not actually present in the normative register
- markdown parsing could become brittle if it depends on formatting outside the published table

## Validation steps

- `python scripts/validate_repo_contracts.py --mode validate`
- `python scripts/validate_repo_contracts.py --mode test`
- `python scripts/benchmark_contract_dry_run.py`

## Rollback strategy

Remove the open-questions schema, export, and correspondence checks, then return to markdown-only tracking until a better machine-readable contract is chosen.

## Evidence required for completion

- a checked-in open-questions export exists and is schema-valid
- repository validation proves the export matches the normative markdown register
- validate, test, and benchmark dry-run pass after the change

## Completion evidence

- `python scripts/validate_repo_contracts.py --mode validate` passed on 2026-03-15
- `python scripts/validate_repo_contracts.py --mode test` passed on 2026-03-15
- `python scripts/benchmark_contract_dry_run.py` passed on 2026-03-15
