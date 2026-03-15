# Report Example Fixtures

Status: complete
Owner: Codex
Date: 2026-03-15

## Objective

Add representative schema-valid example report and manifest artifacts, and make the bootstrap repository checker validate them so the repository proves its report contracts are constructible from the written specs.

## Scope

- add checked-in example JSON artifacts for the published report and manifest schemas
- add a `reports/` directory with explanatory documentation for example artifacts
- extend the repository checker to validate the example artifacts against their schemas
- update repository and validation docs to reflect the new checked-in example surface

## Non-goals

- changing schema contents
- adding executable importer, validator, lowering, reconstruction, or benchmark harness code
- turning example artifacts into implementation claims or benchmark evidence

## Touched files

- `plans/report_example_fixtures.md`
- `reports/README.md`
- `reports/examples/*.json`
- `scripts/validate_repo_contracts.py`
- `README.md`
- `VALIDATION_STRATEGY.md`
- `ci/validation_pipeline.md`
- `docs/repository_map.md`

## Invariants that must remain true

- example artifacts remain illustrative and must not be presented as production evidence
- `make validate` remains the blocking top-level repository validation command
- no semantic, profile, preservation, or tier doctrine changes are introduced
- `SCIR-H` remains canonical and `SCIR-L` remains derivative

## Risks

- example artifacts could accidentally overstate current implementation status if not clearly labeled
- schema-instance validation could add an undeclared dependency if the checker is not self-contained

## Validation steps

- `python scripts/validate_repo_contracts.py --mode validate`
- `python scripts/validate_repo_contracts.py --mode test`
- `python scripts/benchmark_contract_dry_run.py`

## Rollback strategy

Remove the checked-in example artifacts and the associated checker logic, then revert the docs to the prior contract-only state.

## Evidence required for completion

- representative example artifacts exist for the published report and manifest schemas
- repository validation checks the example artifacts against their schemas
- validate, test, and benchmark dry-run pass after the change

## Completion evidence

- `python scripts/validate_repo_contracts.py --mode validate` passed on 2026-03-15
- `python scripts/validate_repo_contracts.py --mode test` passed on 2026-03-15
- `python scripts/benchmark_contract_dry_run.py` passed on 2026-03-15
