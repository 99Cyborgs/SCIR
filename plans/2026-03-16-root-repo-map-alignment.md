# SCIR root repo map alignment

Status: complete
Owner: Codex
Date: 2026-03-16

## Objective

Align SCIR's root governance surface with the tightened ALL-MIND incubate schema by adding and enforcing `REPO_MAP.md`.

## Scope

- add a root `REPO_MAP.md` that points operators to the detailed internal repository map
- update SCIR root read-order and validation surfaces to require the new file
- keep existing detailed structure guidance in `docs/repository_map.md`

## Non-goals

- rewriting SCIR semantic specs
- changing validator semantics beyond repository-surface enforcement
- restructuring runtime or planned code roots

## Touched files

- REPO_MAP.md
- AGENTS.md
- README.md
- scripts/validate_repo_contracts.py

## Invariants that must remain true

- `specs/` remains the semantic source of truth
- `docs/repository_map.md` remains the detailed internal structure guide
- repository validation continues to be driven by `make validate`

## Risks

- creating drift between the new root map and the existing detailed map
- tightening validation without updating read-order docs consistently

## Validation steps

- make validate

## Rollback strategy

Remove the new root file and revert the read-order and validator updates if they introduce inconsistent repository guidance.

## Evidence required for completion

- diff review showing root governance-surface alignment
- `python scripts/validate_repo_contracts.py --mode validate` passed
- `python scripts/python_importer_conformance.py --mode validate-fixtures` passed
- `make validate` could not be invoked directly because `make` is not installed in this shell; the two underlying commands from `Makefile` were executed instead
