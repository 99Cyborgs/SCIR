# 2026-04-03 Continuous Trust Hardening

Status: completed
Owner: Codex
Date: 2026-04-03

## Objective

Tighten the existing SCIR MVP so sweep runs are historically comparable, preservation claims are enforced per stage, validator coverage is deeper within the admitted subset, inactive surfaces are structurally fenced off, and CI blocks trust regressions automatically.

## Scope

- extend the existing sweep runner, result schema, and CI integration with persisted artifacts, comparison mode, metric deltas, and decision-grade summaries
- enforce preservation ceilings and stage behavior from the active Tier A corpus instead of treating preservation as report-only metadata
- deepen SCIR-H, SCIR-L, and translation validation inside the current subset only, with new negative fixtures and stable diagnostics
- add structural active-surface markers so deferred or archived paths cannot silently contaminate validation, sweep, or CI execution
- update the relevant docs, schemas, examples, and repository checks so the new enforcement surfaces are explicit and synchronized

## Non-goals

- add new languages, feature tiers, benchmark tracks, or architectural layers
- widen the executable proof loop beyond the current Python and bounded Rust slices
- introduce new services, dependencies, or parallel artifact systems
- convert deferred documentation into active implementation commitments

## Touched files

- `plans/2026-04-03-continuous-trust-hardening.md`
- `schemas/corpus_manifest.schema.json`
- `schemas/preservation_report.schema.json`
- `schemas/sweep_result.schema.json`
- `reports/examples/*.json` for updated preservation and sweep examples
- `reports/README.md`
- `scripts/scir_bootstrap_pipeline.py`
- `scripts/scir_sweep.py`
- `scripts/run_repo_validation.py`
- `scripts/validate_repo_contracts.py`
- `.github/workflows/validate.yml`
- `.github/workflows/benchmarks.yml`
- `ci/validation_pipeline.md`
- `ci/benchmark_pipeline.md`
- `VALIDATION_STRATEGY.md`
- `BENCHMARK_STRATEGY.md`
- `validators/validator_contracts.md`
- `specs/validator_invariants.md`
- `specs/interop_and_opaque_boundary_spec.md`
- `specs/type_effect_capability_model.md`
- `specs/ownership_alias_model.md`
- `tests/corpora/*.json`
- `tests/invalid_scir_h/*`
- `tests/invalid_scir_l/*`
- `tests/sweeps/*.json`
- deferred or archived paths that need `NOT_ACTIVE.md`

## Invariants that must remain true

- `SCIR-H` remains the only normative semantic source of truth
- `SCIR-L` remains derivative and may not acquire semantics not justified by validated `SCIR-H`
- the active executable path remains the fixed Python proof loop plus bounded Rust importer evidence only
- preservation, boundary, unsupported, and tier claims remain explicit and profile-qualified
- deferred or archived TypeScript and tooling surfaces must stay off the default validation, sweep, and benchmark paths
- `python scripts/run_repo_validation.py` remains the canonical Windows-safe validation entrypoint

## Risks

- sweep artifact persistence and comparison can drift from the current result contract if schemas, examples, CI uploads, and repo checks are not updated together
- preservation enforcement may expose latent overclaims in existing reports, corpora, or fixture metadata and require synchronized fixes across multiple layers
- tighter validator checks can destabilize current fixtures if negative coverage and diagnostic expectations are not updated in lockstep
- structural narrowing markers can create false positives if repository contract checks do not clearly distinguish active and deferred paths

## Validation steps

- `python scripts/validate_repo_contracts.py --mode validate`
- `python scripts/python_importer_conformance.py --mode validate-fixtures`
- `python scripts/rust_importer_conformance.py --mode validate-fixtures`
- `python scripts/scir_bootstrap_pipeline.py --mode validate`
- `python scripts/scir_sweep.py --manifest tests/sweeps/python_proof_loop_smoke.json`
- `python scripts/scir_sweep.py --manifest tests/sweeps/python_proof_loop_full.json`
- `python scripts/run_repo_validation.py`
- `python scripts/benchmark_contract_dry_run.py`

## Rollback strategy

Back out the trust-hardening edits as a coordinated slice if the new enforcement surfaces cannot stay aligned with the current MVP path, then re-land in smaller slices beginning with schema-backed preservation enforcement before historical comparison and CI gates.

## Evidence required for completion

- sweep runs persist to a stable artifact location, compare against a prior run, and emit machine-readable plus human-readable regression summaries
- Tier A corpus fixtures encode enforceable preservation ceilings and stage behavior, and silent preservation drift fails validation
- new negative fixtures cover deeper capability, effect, ownership or alias, opaque-boundary, and provenance checks inside the admitted subset
- sweep summaries aggregate by construct family, diagnostic code, and stage, and expose slice scoring plus ranked slices
- deferred or archived surfaces are physically marked and excluded from active validation and sweep paths
- CI blocks validator-pass, opaque-fraction, preservation, and diagnostic-stability regressions and uploads the generated sweep summaries

## Completion evidence

- Implemented persisted sweep artifacts plus `--compare`, `sweep_summary.*`, and `regression_summary.*` in `scripts/scir_sweep.py`
- Added corpus-backed preservation-stage expectations and active enforcement in `scripts/scir_bootstrap_pipeline.py`, `schemas/corpus_manifest.schema.json`, and the active proof-loop corpora
- Added deeper negative coverage for unused effects, missing throw propagation, borrow-mode mutation, boundary metadata omissions, and provenance-root mismatch under `tests/invalid_scir_h/` and `tests/invalid_scir_l/`
- Added structural `NOT_ACTIVE.md` markers for deferred frontend, tests, tooling, and script surfaces plus repo-contract enforcement in `scripts/validate_repo_contracts.py`
- Wired baseline sweep comparison and regression gates into `.github/workflows/validate.yml` and `.github/workflows/benchmarks.yml`
- Validated with:
  - `python scripts/validate_repo_contracts.py --mode validate`
  - `python scripts/validate_repo_contracts.py --mode test`
  - `python scripts/python_importer_conformance.py --mode validate-fixtures`
  - `python scripts/python_importer_conformance.py --mode test`
  - `python scripts/rust_importer_conformance.py --mode validate-fixtures`
  - `python scripts/rust_importer_conformance.py --mode test`
  - `python scripts/scir_bootstrap_pipeline.py --mode validate`
  - `python scripts/scir_bootstrap_pipeline.py --mode test`
  - `python scripts/scir_sweep.py --manifest tests/sweeps/python_proof_loop_smoke.json --output-dir artifacts/test-sweep-smoke`
  - `python scripts/scir_sweep.py --manifest tests/sweeps/python_proof_loop_smoke.json --output-dir artifacts/test-sweep-compare --compare artifacts/test-sweep-smoke --enforce-regression-gates`
  - `python scripts/scir_sweep.py --manifest tests/sweeps/python_proof_loop_full.json --output-dir artifacts/test-sweep-full`
  - `python scripts/run_repo_validation.py`
