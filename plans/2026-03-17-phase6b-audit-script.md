# Phase 6B Audit Script

Status: complete
Owner: Codex
Date: 2026-03-17

## Objective

Add a focused Phase 6B audit entrypoint that finds remaining sign-off gaps in the current repo state without changing canonical semantics.

## Scope

- add `scripts/phase6b_audit.py` as a diagnostic entrypoint
- audit canonical profile-bearing surfaces for residual monolithic profile `D` usage
- reuse existing benchmark doctrine and executable Track `D` validation logic
- run repeated standalone benchmark checks sequentially and report stability

## Non-goals

- changing `SCIR-H` or `SCIR-L` semantics
- changing benchmark gates or thresholds
- promising concurrency safety for overlapping benchmark-heavy commands
- adding a new subsystem or directory

## Touched files

- `plans/2026-03-17-phase6b-audit-script.md`
- `scripts/phase6b_audit.py`

## Invariants that must remain true

- `SCIR-H` remains the semantic source of truth
- `SCIR-L` remains frozen for Phase 6B semantics
- Track `D` remains executable only for Rust `N` and Python `D-PY`
- `D-JS` remains doctrine-only
- the audit script remains diagnostic and reuses existing validators and benchmark helpers

## Risks

- legacy-profile detection can overmatch valid Tier `D` or Track `D` references
- repeated benchmark execution can lengthen validation time
- audit logic can drift if it duplicates benchmark contract logic instead of reusing it

## Validation steps

- `python scripts/phase6b_audit.py`
- `python scripts/phase6b_audit.py --runs 3`
- `python scripts/phase6b_audit.py --json`
- `python scripts/phase6b_audit.py --runs 3`

## Rollback strategy

Remove `scripts/phase6b_audit.py` and this plan if the audit entrypoint proves redundant or too brittle, while keeping the existing benchmark and validation entrypoints unchanged.

## Evidence required for completion

- a standalone `scripts/phase6b_audit.py` entrypoint exists
- the script reuses existing Phase 6B benchmark validation helpers
- the script reports repeated sequential benchmark status and Track `D` metrics
- the script can fail on injected legacy profile `D`, unexpected executable `D-JS`, and repeated-run instability

## Completion evidence

- `scripts/phase6b_audit.py` exists and reuses `run_benchmark_suite`, benchmark doctrine checks, and executable bundle validation from the existing Phase 6B scripts
- `python scripts/phase6b_audit.py` passed on 2026-03-17
- `python scripts/phase6b_audit.py --runs 3` passed twice on 2026-03-17 on unchanged inputs
- `python scripts/phase6b_audit.py --json` passed on 2026-03-17
- `python scripts/phase6b_audit.py --mode test --runs 1` passed on 2026-03-17 and exercised negative checks for legacy profile `D`, unexpected executable `D-JS`, and repeated-run instability
- `python scripts/validate_repo_contracts.py --mode validate` passed on 2026-03-17
- `python scripts/python_importer_conformance.py --mode validate-fixtures` passed on 2026-03-17
- `python scripts/rust_importer_conformance.py --mode validate-fixtures` passed on 2026-03-17
- `python scripts/scir_bootstrap_pipeline.py --mode test` passed on 2026-03-17
- `python scripts/scir_bootstrap_pipeline.py --language rust --mode test` passed on 2026-03-17
- `python scripts/benchmark_contract_dry_run.py` passed on 2026-03-17
- `python scripts/run_repo_validation.py --require-rust` passed on 2026-03-17
- `make validate` passed on 2026-03-17
- `make benchmark` passed on 2026-03-17
- `scripts/phase6b_audit.py` now uses an explicit Phase 6B surface registry for schemas, examples, exports, Phase 6B markdown, and Python importer fixture manifests instead of ad hoc surface discovery
- missing Python fixture `module_manifest.json` files now surface as audit findings instead of being silently skipped
- `python scripts/phase6b_audit.py --mode test --runs 1` now reuses the first successful benchmark bundle instead of re-running a fresh benchmark pass for self-test setup
- `scripts/scir_bootstrap_pipeline.py` now tolerates Windows Rust Track `D` temp-directory cleanup races without changing benchmark metrics or gate logic
- `python scripts/phase6b_audit.py --runs 1` passed on 2026-03-18
- `python scripts/phase6b_audit.py` passed on 2026-03-18
- `python scripts/phase6b_audit.py --json` passed on 2026-03-18
- `python scripts/phase6b_audit.py --mode test --runs 1` passed on 2026-03-18
- `python scripts/benchmark_contract_dry_run.py` passed on 2026-03-18 when run sequentially
- `python scripts/run_repo_validation.py --require-rust` passed on 2026-03-18
- `make benchmark` passed on 2026-03-18
