# REPO_MAP
Status: Informative

## Root operating surface

- `README.md`: repository purpose and command contract
- `CURRENT_FOCUS.md`: one active bounded item
- `BACKLOG.md`: ranked deferred work
- `ARCHITECTURE.md`: stable system shape
- `DECISION_REGISTER.md`: architectural decisions only
- `VALIDATION_STRATEGY.md`: default validation gate
- `BENCHMARK_STRATEGY.md`: retained benchmark doctrine

## Main working areas

- `specs/`: normative semantics and validator-facing contracts
- `schemas/`: schema contracts for retained reports and manifests
- `scir/`: minimal shared package surface
- `scripts/`: executable bootstrap, validation, and benchmark helpers
- `tests/`: importer fixtures, corpora, and invalid examples
- `validators/`: validator implementations and contracts
- `runtime/`: bounded execution helpers used by retained validation surfaces
- `reports/examples/`: curated schema-valid examples
- `plans/`: plan template plus the current active consolidation plan

## Noise policy

- repeated run outputs belong under ignored `artifacts/`
- derived exports are not part of the live surface
- historical plans are not active authority unless referenced by `CURRENT_FOCUS.md`
