# Repository Hydration

Status: complete
Owner: Codex
Date: 2026-03-15

## Objective

Materialize the packaged SCIR artifact repository into the workspace unchanged and verify that the extracted repository satisfies its bootstrap validation contract.

## Scope

- extract the authoritative `scir/` tree from the packaged artifact
- verify required files are present in the hydrated repository
- run bootstrap validation and benchmark dry-run commands
- record the resulting repository-ready state for follow-on implementation work

## Non-goals

- changing SCIR semantics
- editing specs, schemas, or doctrine files
- implementing parser, importer, validator, lowering, reconstruction, or benchmark harness code

## Touched files

- `plans/repo_hydration.md`
- hydrated repository files under the extracted `scir/` tree

## Invariants that must remain true

- the extracted repository content matches the packaged artifact
- no semantic or scope claims change during hydration
- `SCIR-H` remains canonical and `SCIR-L` remains derivative
- bootstrap validation and benchmark doctrine checks stay green

## Risks

- local extraction could diverge from the packaged artifact if files are overwritten inconsistently
- the environment may lack `make`, requiring direct Python entrypoints for verification

## Validation steps

- `python scripts/validate_repo_contracts.py --mode validate`
- `python scripts/benchmark_contract_dry_run.py`

## Rollback strategy

Remove the extracted `scir/` directory and re-extract it from `scir_foundry_repo.zip`.

## Evidence required for completion

- extracted `scir/` tree present in the workspace
- bootstrap validation passes
- benchmark doctrine dry-run passes
- repository state summary recorded for the next implementation slice

## Completion evidence

- extracted `scir/` tree is present at the workspace root
- `python scripts/validate_repo_contracts.py --mode validate` passed on 2026-03-15
- `python scripts/benchmark_contract_dry_run.py` passed on 2026-03-15
