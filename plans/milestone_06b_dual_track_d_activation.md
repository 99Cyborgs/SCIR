# Milestone 06B - Dual Track D Activation and Dynamic-Host Split

Status: complete
Owner: Codex
Date: 2026-03-17

## Objective

Calibrate Phase 6B into an executable milestone by splitting the dynamic-host profile, adding profile-gated `SCIR-L` optimization doctrine, and activating fixed-corpus Track `D` benchmark slices for Rust `N` and Python `D-PY`.

## Scope

- split profile `D` into `D-PY` and `D-JS`
- update doctrine, schemas, examples, validator expectations, and benchmark contracts for the new profiles
- add benchmark-only `SCIR-L` emitters and profile-gated optimization over the frozen bootstrap op set
- add executable Track `D` bundles for Rust `N` and Python `D-PY`
- rewrite Phase 6B milestone wording to defer witness-bearing second-language execution explicitly

## Non-goals

- adding a new frontend
- widening the canonical `SCIR-L` op set
- replacing `SCIR-H`-driven reconstruction with `SCIR-L` emission
- making `D-JS` executable in this milestone
- turning opaque Tier `C` cases into gating performance kernels

## Touched files

- `IMPLEMENTATION_PLAN.md`
- `README.md`
- `SYSTEM_BOUNDARY.md`
- `ARCHITECTURE.md`
- `DECISION_REGISTER.md`
- `OPEN_QUESTIONS.md`
- `BENCHMARK_STRATEGY.md`
- `VALIDATION_STRATEGY.md`
- `docs/scir_l_overview.md`
- `docs/target_profiles.md`
- `docs/runtime_doctrine.md`
- `docs/preservation_contract.md`
- `docs/reconstruction_policy.md`
- `specs/scir_l_spec.md`
- `specs/validator_invariants.md`
- `validators/translation/AGENTS.md`
- `validators/validator_contracts.md`
- `benchmarks/tracks.md`
- `benchmarks/success_failure_gates.md`
- `benchmarks/baselines.md`
- `benchmarks/corpora_policy.md`
- `ci/benchmark_pipeline.md`
- `schemas/benchmark_manifest.schema.json`
- `schemas/benchmark_result.schema.json`
- `schemas/profile_claim.schema.json`
- `schemas/preservation_report.schema.json`
- `schemas/reconstruction_report.schema.json`
- `schemas/module_manifest.schema.json`
- `scripts/scir_bootstrap_pipeline.py`
- `scripts/benchmark_contract_dry_run.py`
- `scripts/run_repo_validation.py`
- `scripts/validate_repo_contracts.py`
- `scripts/scir_python_bootstrap.py`
- `scripts/python_importer_conformance.py`
- `reports/README.md`
- `reports/exports/decision_register.export.json`
- `reports/exports/open_questions.export.json`
- `tests/python_importer/cases/*/module_manifest.json`
- `plans/milestone_03_l_lowering.md`
- `plans/milestone_04_reconstruction.md`

## Invariants that must remain true

- `SCIR-H` remains the semantic source of truth
- `SCIR-L` remains derivative and does not gain new canonical ops
- reconstruction remains `SCIR-H`-driven
- benchmark-only emitters stay non-normative and do not become de facto reconstruction paths
- Track `A` and Track `B` behavior remains intact aside from `D-PY` replacing monolithic `D`
- `D-JS` remains doctrine-only in Phase 6B

## Risks

- benchmark-only emitters drift into backend surface area
- profile-split churn leaves stale monolithic `D` references in validators or examples
- Track `D` microbench timing is noisy on the Windows/Python execution path
- milestone wording remains inconsistent if witness deferral is not made explicit everywhere

## Validation steps

```bash
python scripts/validate_repo_contracts.py --mode validate
python scripts/python_importer_conformance.py --mode validate-fixtures
python scripts/rust_importer_conformance.py --mode validate-fixtures
python scripts/scir_bootstrap_pipeline.py --mode test
python scripts/scir_bootstrap_pipeline.py --language rust --mode test
python scripts/benchmark_contract_dry_run.py
python scripts/run_repo_validation.py --require-rust
make validate
make benchmark
```

## Rollback strategy

Revert Phase 6B to doctrine-only status by removing executable Track `D` bundles, restoring the pre-6B benchmark checker expectations, and leaving the profile split and witness deferral explicitly recorded only if the benchmark activation cannot be made credible.

## Evidence required for completion

- profile-bearing schemas and example reports migrated from `D` to `D-PY`/`D-JS`
- decision register entry for the profile split and executable Track `D` activation
- open-question update resolving OQ-002 and OQ-004 or superseding them explicitly
- passing executable Track `D` bundles for Rust `N` and Python `D-PY`
- confirmation that reconstruction remains `SCIR-H`-driven and Track `A`/`B` still pass

## Completion evidence

- `python scripts/validate_repo_contracts.py --mode validate` passed on 2026-03-17
- `python scripts/python_importer_conformance.py --mode validate-fixtures` passed on 2026-03-17
- `python scripts/rust_importer_conformance.py --mode validate-fixtures` passed on 2026-03-17
- `python scripts/scir_bootstrap_pipeline.py --mode test` passed on 2026-03-17
- `python scripts/scir_bootstrap_pipeline.py --language rust --mode test` passed on 2026-03-17
- `python scripts/benchmark_contract_dry_run.py` passed on 2026-03-17 with executable Track `A`, `B`, Rust `N` Track `D`, and Python `D-PY` Track `D` bundles
- `python scripts/run_repo_validation.py --require-rust` passed on 2026-03-17
- `make validate` passed on 2026-03-17
- `make benchmark` passed on 2026-03-17
- monolithic profile `D` is now rejected by schemas, validator expectations, checked-in Python manifests, and benchmark contract self-tests
- Phase 6B now keeps `SCIR-L` op semantics frozen while allowing only the published `N` and `D-PY` optimization rewrites plus benchmark-only post-`SCIR-L` emitters
- executable Track `D` is limited to Rust `N` and Python `D-PY`; `D-JS` and witness-bearing second-language execution remain explicitly deferred
