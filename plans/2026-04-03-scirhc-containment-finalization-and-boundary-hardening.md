# 2026-04-03 SCIR-Hc Containment Finalization and Boundary Hardening

Status: complete
Owner: Codex
Date: 2026-04-03

## Objective

Close the remaining SCIR-Hc containment gaps by making transform access internal and context-bound, binding derived artifacts to canonical SCIR-H lineage plus normalized hashes, classifying benchmark metrics to block authority leakage, extending round-trip enforcement to explicit semantic idempotence, and emitting a structural SCIR-H -> SCIR-Hc diff audit without changing SCIR-H semantics, SCIR-Hc IR shape, or pipeline architecture.

## Scope

- move executable SCIR-Hc transforms behind an internal module and fail-closed call gate
- require generation context on SCIR-Hc transform entrypoints
- bind SCIR-Hc report artifacts and benchmark evidence to canonical SCIR-H lineage plus normalized hashes
- require metric classification and explicit SCIR-H evidence mapping on benchmark claim surfaces
- extend validator and benchmark paths with explicit semantic-idempotence checks
- generate and publish `scirhc_diff_audit.json` in report-producing paths
- expand doctrine tests for unauthorized access, context failure, lineage spoofing, coverage gaps, metric authority leakage, and round-trip drift

## Non-goals

- changing canonical SCIR-H semantics or grammar
- changing the SCIR-Hc IR shape
- adding a new representation or widening pipeline architecture
- relaxing any existing SCIR-Hc containment rule into warning-only behavior

## Touched files

- `plans/2026-04-03-scirhc-containment-finalization-and-boundary-hardening.md`
- `_internal/scirhc_transform.py`
- `_internal/__init__.py`
- `scripts/scir_h_bootstrap_model.py`
- `scripts/scir_bootstrap_pipeline.py`
- `scripts/benchmark_contract_dry_run.py`
- `schemas/benchmark_report.schema.json`
- `reports/examples/benchmark_report.example.json`
- `specs/scir_hc_doctrine.md`
- `specs/validator_invariants.md`
- `VALIDATION_STRATEGY.md`
- `BENCHMARK_STRATEGY.md`
- `validators/scirhc_validator.py`
- `validators/validator_contracts.md`
- `docs/SCIR_HC_FAILURE_MODES.md`
- `tests/test_scirhc_doctrine.py`

## Invariants that must remain true

- `SCIR-H` remains the only semantic source of truth
- `SCIR-Hc` remains derived-only, report-only, and non-executable
- no downstream lowering, reconstruction, backend emission, or semantic authority may originate from stored `SCIR-Hc`
- all SCIR-Hc enforcement remains validator-driven and fail-closed
- canonical `SCIR-H -> SCIR-Hc -> SCIR-H` normalization remains exact

## Risks

- internalization can break existing trusted call sites if every transform consumer is not migrated together
- lineage hardening can drift between validator logic, schema, report generator, and example artifact
- metric-class enforcement can reject the current benchmark payload if classification and evidence mapping are not synchronized
- diff-audit generation can bloat report outputs if the structural summary is not kept minimal and canonical

## Validation steps

- `python -m py_compile validators/scirhc_validator.py`
- `python -m unittest discover -s tests -p test_scirhc_doctrine.py`
- `python scripts/scir_bootstrap_pipeline.py --mode validate`
- `python scripts/benchmark_contract_dry_run.py`
- `python scripts/validate_repo_contracts.py --mode validate`

## Rollback strategy

Revert the hardening slice as one unit so the internal transform gate, validator rules, benchmark schema, report generator, and doctrine tests return to the last synchronized state instead of leaving partial containment rules behind.

## Evidence required for completion

- unauthorized or out-of-context SCIR-Hc transform access fails with hard errors
- SCIR-Hc lineage references include canonical module identity plus normalized canonical hash and are validator-checked
- benchmark claim surfaces require metric classification plus explicit SCIR-H evidence mapping and reject authority leakage
- validator and benchmark paths both execute semantic-idempotence enforcement
- `scirhc_diff_audit.json` is generated and referenced from report outputs
- all listed validation commands pass

## Completion evidence

- `python -m py_compile validators/scirhc_validator.py` passed
- `python -m unittest discover -s tests -p test_scirhc_doctrine.py` passed
- `python scripts/scir_bootstrap_pipeline.py --mode validate` passed
- `python scripts/benchmark_contract_dry_run.py` passed and wrote artifacts under `artifacts/benchmark_runs/python-proof-loop-full-20260403T193945Z`
- `python scripts/validate_repo_contracts.py --mode validate` passed
