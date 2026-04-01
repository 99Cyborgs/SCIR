# Windows Rust Temp Cleanup

Status: complete
Owner: Codex
Date: 2026-03-21

## Objective

Make the Rust reconstruction validation path tolerant of Windows temp-directory cleanup races so the canonical repo validation entrypoint can complete reliably.

## Scope

- patch the Rust reconstruction temp-directory lifecycle in `scripts/scir_bootstrap_pipeline.py`
- verify the fix through the affected validation commands

## Non-goals

- changing `SCIR-H` or `SCIR-L` semantics
- changing benchmark metrics, gates, or profile claims
- broadening Rust subset scope
- adding new executable benchmark cases

## Touched files

- `plans/2026-03-21-windows-rust-temp-cleanup.md`
- `scripts/scir_bootstrap_pipeline.py`

## Invariants that must remain true

- `SCIR-H` remains the semantic source of truth
- Rust validation and benchmark behavior remain semantically unchanged
- the fix only addresses temp cleanup reliability on Windows

## Risks

- over-broad cleanup suppression could hide a real pipeline failure
- the fix could diverge from the existing Rust Track `D` tempdir handling if implemented differently

## Validation steps

- `python scripts/scir_bootstrap_pipeline.py --language rust --mode validate`
- `python scripts/benchmark_contract_dry_run.py`
- `python scripts/run_repo_validation.py --require-rust`

## Rollback strategy

Revert the temp-directory handling change and this plan if the fix masks substantive Rust pipeline errors or introduces new validation drift.

## Evidence required for completion

- Rust reconstruction validation completes without Windows temp cleanup failures
- benchmark dry run completes without Windows temp cleanup failures
- repo validation completes through the Rust-inclusive path

## Completion evidence

- `python scripts/scir_bootstrap_pipeline.py --language rust --mode validate` passed on 2026-03-21
- `python scripts/benchmark_contract_dry_run.py` passed on 2026-03-21
- `python scripts/run_repo_validation.py --require-rust` passed on 2026-03-21
- `scripts/scir_bootstrap_pipeline.py` now uses Windows-tolerant temp-directory cleanup for Rust reconstruction validation, matching the existing Rust Track `D` tempdir posture without changing validation or benchmark semantics
