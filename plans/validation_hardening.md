# Validation Hardening

Status: complete
Owner: Codex
Date: 2026-03-15

## Objective

Strengthen the bootstrap repository contract checker so it enforces more of the existing validation and checker contracts without changing SCIR semantics.

## Scope

- add validator invariant coverage checks for `specs/validator_invariants.md`
- add report-schema completeness checks for repository report and manifest schemas
- keep the command contract unchanged

## Non-goals

- changing `SCIR-H` or `SCIR-L` semantics
- adding executable `SCIR-H`, `SCIR-L`, or translation validators
- changing schema contents
- changing benchmark doctrine

## Touched files

- `plans/validation_hardening.md`
- `scripts/validate_repo_contracts.py`

## Invariants that must remain true

- `SCIR-H` remains canonical and `SCIR-L` remains derivative
- repository validation stays blocking on hard contract failures
- no new semantic claims are introduced
- bootstrap validation remains runnable through the existing script entrypoint

## Risks

- the checker could become brittle if it overfits to markdown formatting instead of contract content
- stricter checks could fail valid future docs if they are implemented too rigidly

## Validation steps

- `python scripts/validate_repo_contracts.py --mode validate`
- `python scripts/validate_repo_contracts.py --mode test`
- `python scripts/benchmark_contract_dry_run.py`

## Rollback strategy

Revert the new checker routines and return to the previous file-presence and JSON-parseability checks, then record any remaining desired checks as a follow-on plan.

## Evidence required for completion

- invariant coverage checks are implemented and passing
- report-schema completeness checks are implemented and passing
- bootstrap validation and benchmark dry-run pass after the change

## Completion evidence

- `python scripts/validate_repo_contracts.py --mode validate` passed on 2026-03-15
- `python scripts/validate_repo_contracts.py --mode test` passed on 2026-03-15
- `python scripts/benchmark_contract_dry_run.py` passed on 2026-03-15
