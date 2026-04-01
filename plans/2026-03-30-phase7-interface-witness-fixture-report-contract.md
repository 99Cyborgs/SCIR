# Phase 7 Interface-Witness Fixture and Report Contract

Status: complete
Owner: Codex
Date: 2026-03-30

## Objective

Define the minimum checked-in fixture bundle and report obligations for the first importer-only TypeScript interface witness slice before any TypeScript importer implementation begins.

## Scope

- define the accepted first-slice source shape as module-level `interface` declarations plus module-local witness consumption examples
- define the checked-in fixture bundle shape and required report artifacts for admitted and rejected TypeScript Phase 7 cases
- define the rejection boundary for nearby out-of-scope constructs such as functions, `async`, classes, prototype behavior, decorators, proxies, and executable type-level semantics
- update the active milestone and queue surfaces so the fixture/report-definition slice is explicit and complete

## Non-goals

- implementing a TypeScript importer
- adding executable `D-JS`, `SCIR-L`, translation, reconstruction, or benchmark artifacts
- changing schemas unless the existing report contracts prove insufficient

## Touched files

- `plans/2026-03-30-phase7-interface-witness-fixture-report-contract.md`
- `plans/milestone_07_typescript_witness_slice.md`
- `frontend/typescript/IMPORT_SCOPE.md`
- `VALIDATION_STRATEGY.md`
- `tests/README.md`
- `frontend/README.md`
- `EXECUTION_QUEUE.md`
- `reports/exports/execution_queue.export.json`

## Invariants that must remain true

- the first Phase 7 slice remains importer-only and non-executable
- existing `module_manifest`, `feature_tier_report`, and `validation_report` contracts remain the default evidence package
- the first TypeScript fixture bundle stays narrower than the already-bounded doctrine

## Risks

- the fixture contract could accidentally imply that TypeScript importer code already exists
- bundle wording could drift from the Python/Rust fixture model and create a parallel artifact convention

## Validation steps

- `python scripts/build_execution_queue.py --mode check`
- `python scripts/validate_repo_contracts.py --mode validate`
- `python scripts/run_repo_validation.py`

## Rollback strategy

Revert the fixture/report doctrine and queue updates together if the new wording widens executable scope or introduces a TypeScript-specific artifact model that diverges from the repository fixture conventions.

## Evidence required for completion

- the active Phase 7 milestone names the minimum checked-in evidence package for the first TypeScript slice
- TypeScript scope, frontend doctrine, tests doctrine, and validation doctrine agree on the fixture/report bundle shape and rejection boundary
- `Q-07-003` is complete and the next bounded Phase 7 item is explicit

## Completion evidence

- `plans/milestone_07_typescript_witness_slice.md` now names the first evidence package for the TypeScript interface-witness slice
- `frontend/typescript/IMPORT_SCOPE.md`, `frontend/README.md`, `tests/README.md`, and `VALIDATION_STRATEGY.md` now agree on the first-slice bundle shape and rejection boundary
- `EXECUTION_QUEUE.md` now marks `Q-07-003` complete and makes `Q-07-004` the next ready Phase 7 item
- `python scripts/build_execution_queue.py --mode check` passed on `2026-03-30`
- `python scripts/validate_repo_contracts.py --mode validate` passed on `2026-03-30`
- `python scripts/run_repo_validation.py` passed on `2026-03-30`
