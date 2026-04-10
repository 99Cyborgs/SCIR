# Repository Reset Report

## What was kept

- normative semantic specs under `specs/`
- schema contracts under `schemas/`
- executable bootstrap, validator, importer, sweep, and benchmark scripts under `scripts/`
- importer fixtures, corpora, sweep manifests, and invalid examples under `tests/`
- bounded retained support surfaces for Rust importer evidence, `SCIR-L`, Wasm, and benchmark doctrine
- curated report examples under `reports/examples/`

## What was removed

- tracked timestamped sweep outputs under `artifacts/`
- tracked timestamped benchmark run and repro outputs under `artifacts/`
- queue-era control surface files:
  - `EXECUTION_QUEUE.md`
  - `scripts/build_execution_queue.py`
  - `schemas/execution_queue.schema.json`
  - `reports/exports/*`
- redundant root posture files that no longer define the live path:
  - `ARCHITECTURE_SUMMARY.md`
  - `ROADMAP.md`
  - `STATUS.md`
  - `VALIDATION.md`
  - `MVP_SCOPE.md`
  - `DEFERRED_COMPONENTS.md`
  - `DEPENDENCY_NOTES.md`
  - `INTEGRATION_RISKS.md`
  - `PROMOTION_NOTES.md`
- stale historical plans in `plans/`

## What was archived

- historical planning detail was reduced to `plans/PLANS.md` plus the active consolidation plan
- repeated run outputs were moved out of the tracked repository surface by deletion plus ignore rules

## What was salvaged from `codex/validation-hardening-worktree`

- `pyproject.toml` as a minimal package and dependency boundary for the executable repo
- a minimal `scir/__init__.py` package surface so the hot path includes an actual package root

No other branch-only changes were retained. The remaining unique branch diff was dominated by generated artifacts, release-oriented machinery, and governance-heavy churn that did not improve the executable MVP path.

## What remains intentionally deferred

- grammar widening beyond the current admitted subset
- release-bundle activation in default workflows
- new frontends or broader backend claims
- promotion of Track `C`
- native or host-runtime parity claims

## Single active MVP target

`Python subset importer -> canonical SCIR-H -> validator hardening`
