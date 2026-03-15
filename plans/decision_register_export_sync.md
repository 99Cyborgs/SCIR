# Decision Register Export Sync

Status: complete
Owner: Codex
Date: 2026-03-15

## Objective

Create a checked-in decision-register JSON export derived from the normative markdown register and make repository validation prove the markdown, schema, and export stay synchronized.

## Scope

- resolve the current mismatch between `DECISION_REGISTER.md` and `schemas/decision_register.schema.json`
- add a checked-in derived decision-register export under `reports/`
- extend the repository checker to parse the markdown register, validate the export, and fail on drift
- update validation-facing docs to describe the derived export surface

## Non-goals

- changing repository architecture decisions themselves
- adding a general markdown-to-json export framework for unrelated files
- changing benchmark doctrine or SCIR semantics

## Touched files

- `plans/decision_register_export_sync.md`
- `schemas/decision_register.schema.json`
- `reports/README.md`
- `reports/exports/decision_register.export.json`
- `scripts/validate_repo_contracts.py`
- `README.md`
- `VALIDATION_STRATEGY.md`
- `ci/validation_pipeline.md`
- `docs/repository_map.md`

## Invariants that must remain true

- `DECISION_REGISTER.md` remains the normative human-readable source
- the checked-in export is derived, not independently authored
- `make validate` remains the blocking top-level validation command
- no architecture decision text is silently reinterpreted during export

## Risks

- schema changes could accidentally weaken the decision-register contract instead of aligning it
- markdown parsing could become brittle if it depends on incidental formatting outside the published table

## Validation steps

- `python scripts/validate_repo_contracts.py --mode validate`
- `python scripts/validate_repo_contracts.py --mode test`
- `python scripts/benchmark_contract_dry_run.py`

## Rollback strategy

Remove the derived export and correspondence checks, restore the prior schema, and keep the decision-register mismatch explicit until a better contract is chosen.

## Evidence required for completion

- a checked-in decision-register export exists and is schema-valid
- repository validation proves the export matches the normative markdown register
- validate, test, and benchmark dry-run pass after the change

## Completion evidence

- `python scripts/validate_repo_contracts.py --mode validate` passed on 2026-03-15
- `python scripts/validate_repo_contracts.py --mode test` passed on 2026-03-15
- `python scripts/benchmark_contract_dry_run.py` passed on 2026-03-15
