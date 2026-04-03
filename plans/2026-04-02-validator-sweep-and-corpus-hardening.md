# 2026-04-02 Validator, Sweep, and Corpus Hardening

Status: complete
Owner: Codex
Date: 2026-04-02

## Objective

Harden the existing narrow SCIR MVP for serious internal testing by adding stable invariant-coded validator failures, fixture-driven negative validation lanes, manifest-governed corpus metadata, a slice-based sweep runner, and CI/documentation updates that reflect those executable surfaces truthfully.

## Scope

- keep the active supported subset unchanged while making validator failures more explicit and machine-aggregable
- add seeded negative `SCIR-H` and `SCIR-L` fixtures keyed to the published validator invariants
- add machine-readable fixture and corpus manifests for the active proof-loop corpus
- add a slice-based sweep manifest, result schema, runner, and summary generation over the fixed active corpus
- wire a tiny sweep smoke lane into validation and separate fast correctness from slower evaluation in CI
- update root and validation/benchmark/test docs so the new active hardening surfaces are explicit

## Non-goals

- widen language support beyond the active Python and Rust subsets
- broaden the executable proof loop beyond the current fixed cases
- add new production dependencies, services, or backend semantics
- claim artifact-history regression support beyond optional comparison against an explicitly provided prior sweep result

## Touched files

- `README.md`
- `VALIDATION.md`
- `VALIDATION_STRATEGY.md`
- `BENCHMARK_STRATEGY.md`
- `benchmarks/corpora_policy.md`
- `ci/validation_pipeline.md`
- `ci/benchmark_pipeline.md`
- `.github/workflows/validate.yml`
- `.github/workflows/benchmarks.yml`
- `tests/README.md`
- `schemas/validation_report.schema.json`
- `schemas/benchmark_manifest.schema.json`
- `schemas/benchmark_result.schema.json`
- `schemas/*.schema.json` for new fixture, corpus, and sweep contracts
- `reports/README.md`
- `reports/examples/*` for new sweep and corpus examples
- `scripts/scir_bootstrap_pipeline.py`
- `scripts/run_repo_validation.py`
- `scripts/validate_repo_contracts.py`
- `scripts/python_importer_conformance.py`
- `scripts/rust_importer_conformance.py`
- `scripts/*.py` for new sweep and manifest helpers
- `tests/invalid_scir_h/*`
- `tests/*` for new negative `SCIR-L` fixtures and active corpus manifests

## Invariants that must remain true

- `SCIR-H` remains the only normative semantic source of truth
- `SCIR-L` remains derivative and cannot acquire L-only semantics
- active executable cases stay fixed to the current narrow Python proof loop and bounded Rust importer evidence
- unsupported and opaque cases remain explicit and do not silently upgrade into support
- `python scripts/run_repo_validation.py` remains the canonical Windows-safe validation entrypoint

## Risks

- new invariant codes or fixture manifests may drift from existing generated artifact expectations if the repo checks are not updated together
- a sweep layer could duplicate existing benchmark or validation reporting unless it reuses current validator outputs and contracts
- CI job splitting could accidentally widen the default gate or hide failures if fast and slow lane boundaries are not documented and enforced clearly

## Validation steps

- `python scripts/validate_repo_contracts.py --mode validate`
- `python scripts/validate_repo_contracts.py --mode test`
- `python scripts/python_importer_conformance.py --mode validate-fixtures`
- `python scripts/rust_importer_conformance.py --mode validate-fixtures`
- `python scripts/scir_bootstrap_pipeline.py --mode validate`
- `python scripts/scir_bootstrap_pipeline.py --mode test`
- `python scripts/run_repo_validation.py`
- `python scripts/benchmark_contract_dry_run.py`

## Rollback strategy

Revert the validator/sweep/corpus hardening changes as a unit if the new machine-readable surfaces cannot be kept aligned with the existing proof loop, then re-land in smaller slices starting with invariant-coded diagnostics before sweep orchestration and CI changes.

## Evidence required for completion

- fixture-driven negative checks exist for the active published `SCIR-H` and `SCIR-L` invariants
- active proof-loop fixtures and corpora have machine-readable manifests validated by schema
- the sweep runner emits schema-valid structured results and a human-readable summary over the fixed active corpus
- fast validation and slower evaluation lanes are explicitly separated in CI and doctrine
- `make validate` and `make benchmark` still pass on the narrowed MVP without widening supported semantics

## Completion evidence

- `python scripts/scir_bootstrap_pipeline.py --mode validate` passed
- `python scripts/scir_bootstrap_pipeline.py --mode test` passed
- `python scripts/validate_repo_contracts.py --mode validate` passed
- `python scripts/validate_repo_contracts.py --mode test` passed with `44` negative fixtures
- `python scripts/scir_sweep.py --manifest tests/sweeps/python_proof_loop_smoke.json` passed
- `python scripts/scir_sweep.py --manifest tests/sweeps/python_proof_loop_full.json --output-dir artifacts/sweep-full` passed with `22` result rows and one warning cluster `PY-C001`
- `python scripts/benchmark_contract_dry_run.py` passed with Track `A` status `pass`, Track `B` status `pass`, and `24` benchmark negative fixtures
- `python scripts/run_repo_validation.py` passed, including repository contracts, Python importer fixtures, Rust importer fixtures, bootstrap validation, sweep smoke, and benchmark doctrine
