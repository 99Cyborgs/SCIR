# 2026-04-07 Repo Maintainability And Validation Rebalance

Status: complete
Owner: Codex
Date: 2026-04-07

## Objective

Improve maintainability, installability, and validation layering without widening the admitted SCIR MVP or changing the current operator entrypoints.

## Scope

- repair the broken semantic-core self-test lane so `make test` becomes trustworthy again
- extract shared contract and schema helpers out of the repository-governance CLI so semantic-core code no longer imports the monolithic checker script
- split the repository checker into smaller modules while preserving `python scripts/validate_repo_contracts.py`
- add a minimal Python package manifest and package boundary so active code can run from a clean environment without manual path mutation
- render duplicated metadata-backed contract fragments instead of hand-maintaining repeated markdown lists and tables
- isolate deferred Track `D` and other non-MVP residue away from the active proof-loop module
- reduce root-doc sprawl by moving non-normative portfolio notes out of the root while preserving authority docs

## Non-goals

- widen the admitted Python, Rust, Wasm, or benchmark subset
- activate TypeScript, Track `D`, Rust reconstruction, or broader backend claims
- make `SCIR-Hc` or `SCIR-L` a semantic authority
- replace the current CLI/operator entrypoints or `make` targets
- rewrite normative specs or doctrine prose into generated text wholesale

## Touched files

- `plans/2026-04-07-repo-maintainability-and-validation-rebalance.md`
- `pyproject.toml`
- `Makefile`
- `README.md`
- `REPO_MAP.md`
- `VALIDATION.md`
- `VALIDATION_STRATEGY.md`
- `BENCHMARK_STRATEGY.md`
- `LOWERING_CONTRACT.md`
- `SPEC_COMPLETENESS_CHECKLIST.md`
- `backends/wasm/README.md`
- `frontend/python/IMPORT_SCOPE.md`
- `frontend/rust/IMPORT_SCOPE.md`
- `ARCHITECTURE_SUMMARY.md`
- `STATUS.md`
- `PROMOTION_NOTES.md`
- `INTEGRATION_RISKS.md`
- `DEPENDENCY_NOTES.md`
- `.github/workflows/validate.yml`
- `.github/workflows/benchmarks.yml`
- `.github/workflows/validate_scirhc_containment.yml`
- `scripts/run_repo_validation.py`
- `scripts/validate_repo_contracts.py`
- `scripts/benchmark_contract_dry_run.py`
- `scripts/scir_bootstrap_pipeline.py`
- `scripts/scir_h_bootstrap_model.py`
- `scripts/scir_python_bootstrap.py`
- `scripts/scir_rust_bootstrap.py`
- `scripts/benchmark_contract_metadata.py`
- `scripts/wasm_backend_metadata.py`
- `validators/*` for extracted shared helpers and active validator modules
- supporting package or tooling files needed to preserve wrapper-backed CLI behavior

## Invariants that must remain true

- `SCIR-H` remains the only normative semantic representation
- `SCIR-Hc` remains derived-only and may not enter lowering, reconstruction, or backend emission directly
- `SCIR-L` remains derivative-only and justified by validated `SCIR-H` plus named lowering rules
- the active MVP stays limited to canonical `SCIR-H`, derived `SCIR-Hc`, derivative `SCIR-L`, validators, Python subset import, bounded Rust importer evidence, Python reconstruction, bounded Wasm reference backend, and Track `A` / `B`
- Track `C` remains non-default and Track `D` remains deferred
- `python scripts/run_repo_validation.py` remains the canonical Windows-safe validation entrypoint

## Risks

- modularization can create import drift if shared helpers move before wrappers and tests are updated together
- metadata-driven rendering can accidentally flatten normative nuance if generation expands beyond duplicated contract fragments
- package-boundary work can break current direct script execution if wrappers stop resolving local imports correctly
- moving deferred code out of the active pipeline can create hidden CI or self-test dependencies if the split is incomplete
- root-doc cleanup can strand useful navigation if `README.md` and `REPO_MAP.md` are not updated together

## Validation steps

- `python scripts/validate_repo_contracts.py --mode validate`
- `python scripts/validate_repo_contracts.py --mode test`
- `python scripts/python_importer_conformance.py --mode validate-fixtures`
- `python scripts/python_importer_conformance.py --mode test`
- `python scripts/rust_importer_conformance.py --mode validate-fixtures`
- `python scripts/rust_importer_conformance.py --mode test`
- `python scripts/scir_bootstrap_pipeline.py --mode validate`
- `python scripts/scir_bootstrap_pipeline.py --mode test`
- `python -m unittest discover -s tests`
- `python scripts/benchmark_contract_dry_run.py`
- `python scripts/run_repo_validation.py`

## Rollback strategy

Revert the refactor in slices: first restore previous import paths and wrapper behavior, then back out metadata-rendering and root-doc consolidation if they destabilize validation, while keeping the semantic-core self-test fix if it remains isolated and safe.

## Evidence required for completion

- `make test` and the explicit semantic-core test commands run cleanly
- semantic-core scripts no longer depend on the monolithic repository checker script for reusable helper logic
- duplicated benchmark, importer-scope, Wasm, and checklist fragments are metadata-backed rather than hand-synchronized
- a clean Python environment can install and run the repo without ad hoc `sys.path` setup
- deferred Track `D` logic is isolated from the active proof-loop module
- root operator docs are easier to navigate without losing normative authority or command discoverability

## Current evidence

- `python scripts/scir_bootstrap_pipeline.py --mode test` passed after hardening the output-bundle validator against missing keys
- `python -m unittest discover -s tests` passed
- `python scripts/python_importer_conformance.py --mode test` passed
- `python scripts/rust_importer_conformance.py --mode test` passed
- `python scripts/validate_repo_contracts.py --mode validate` passed
- `python scripts/validate_repo_contracts.py --mode test` passed
- `python scripts/run_repo_validation.py` passed
- a throwaway virtual environment successfully ran `pip install -e .[dev]` and imported `scir.contract_docs`
- `scripts/deferred_track_d.py` now owns the dormant Track `D` benchmark and optimization helpers outside the active proof-loop module
- `scripts/scir_bootstrap_pipeline.py` now keeps only thin lazy wrappers for the deferred `run_python_track_d` and `run_rust_track_d` entrypoints
- `scripts/validate_repo_contracts.py` now fails if deferred Track `D` logic drifts back into the active proof-loop module or if the deferred-module marker goes stale
- `scripts/NOT_ACTIVE.md` now lists the deferred Track `D` helper module explicitly
- `python scripts/validate_repo_contracts.py --mode validate` passed after regenerating the required queue/checkpoint exports
- `python scripts/validate_repo_contracts.py --mode test` passed with 59 negative fixtures
- `python scripts/run_repo_validation.py` passed after the deferred-module extraction

## Remaining work

- none

## CLOSEOUT

- Scope completed: the last deferred-surface isolation task is closed, with dormant Track `D` helpers moved out of `scripts/scir_bootstrap_pipeline.py` into `scripts/deferred_track_d.py` while preserving the historical entrypoints through thin wrappers only.
- Invariants satisfied: `SCIR-H` remained the only semantic authority, the active MVP surface and default CLI entrypoints did not widen, and Track `D` stayed explicitly deferred and outside the default validation or benchmark gate.
- Residual risks: the deferred module is still importable for historical/manual use, so any future attempt to reactivate Track `D` still requires explicit governance rather than only code movement.
- Validation status: passed on 2026-04-07 and 2026-04-08 via `python scripts/scir_bootstrap_pipeline.py --mode test`, `python scripts/validate_repo_contracts.py --mode validate`, `python scripts/validate_repo_contracts.py --mode test`, and `python scripts/run_repo_validation.py`.
