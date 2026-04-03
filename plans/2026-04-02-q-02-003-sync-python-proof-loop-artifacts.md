# 2026-04-02 Q-02-003 Sync Python Proof-Loop Artifacts From Metadata

Status: complete
Owner: Codex
Date: 2026-04-02

## Objective

Reduce ordinary proof-loop drift by adding a single sync command that regenerates the Python importer golden artifacts and the checked-in Track `C` sample artifacts directly from the authoritative executable metadata and live runner outputs.

## Scope

- add a sync script for Python proof-loop generated artifacts
- regenerate Python importer checked-in JSON bundles from `scripts/scir_python_bootstrap.py`
- regenerate checked-in Track `C` manifest and result examples from the live optional pilot output
- add validation coverage so drift still fails fast and the sync command surface remains explicit
- document the intended workflow as metadata change -> sync -> validate

## Non-goals

- no widening of Python executable support beyond the current bounded case set
- no Wasm scope change
- no Rust scope change
- no change to default benchmark gate or Track `C` posture

## Touched files

- `scripts/sync_python_proof_loop_artifacts.py`
- `scripts/validate_repo_contracts.py`
- `scripts/benchmark_contract_dry_run.py`
- `README.md`
- `VALIDATION.md`
- `plans/2026-04-01-mvp-narrowing-and-contract-hardening.md`

## Invariants that must remain true

- `scripts/scir_python_bootstrap.py` remains the authoritative source for Python importer bundle generation
- Track `C` examples remain illustrative checked-in samples, not default executable benchmark outputs
- repo validation still fails if checked-in artifacts drift from generated outputs
- the active executable Python proof loop remains bounded to the current case set

## Risks

- a sync command that reimplements generation logic instead of reusing existing generators would create a second source of truth
- documentation could imply the sync command changes benchmark or validation policy instead of only regenerating checked-in examples
- broad repo validation may still fail if the new script surface is undocumented in command guidance

## Validation steps

- `python scripts/sync_python_proof_loop_artifacts.py --mode check`
- `python scripts/sync_python_proof_loop_artifacts.py --mode write`
- `python scripts/python_importer_conformance.py --mode validate-fixtures`
- `python scripts/benchmark_contract_dry_run.py --include-track-c-pilot`
- `python scripts/validate_repo_contracts.py --mode validate`
- `python scripts/validate_repo_contracts.py --mode test`
- `python scripts/run_repo_validation.py --include-track-c-pilot`

## Rollback strategy

Revert the sync script, its documentation, and any validator wiring as one unit if the command cannot be kept as a thin wrapper over the existing authoritative generators.

## Evidence required for completion

- one command regenerates the Python importer goldens and Track `C` sample artifacts from existing authorities
- validator and benchmark checks still fail on drift after regeneration support is added
- the sync workflow is documented without changing default validation or benchmark gates

## Completion evidence

- `scripts/sync_python_proof_loop_artifacts.py` now regenerates the checked-in Python importer artifacts for every fixed proof-loop case by reusing `build_bundle` from `scripts/scir_python_bootstrap.py`
- the same sync command also regenerates the checked-in Track `C` manifest and result examples by reusing the live optional pilot output from `run_track_c_pilot`
- `README.md` and `VALIDATION.md` now document the workflow as metadata change -> `python scripts/sync_python_proof_loop_artifacts.py --mode write` -> validation
- `scripts/validate_repo_contracts.py` now treats the sync command surface as part of the active command contract and self-tests that the documentation marker remains explicit
- the queue now closes `Q-02-003` and points back to a substantive Wasm follow-on instead of optional Track `C` governance
