# 2026-04-03 SCIR-Hc Containment Regression Hardening

Status: complete
Owner: Codex
Date: 2026-04-03

## Objective

Harden SCIR-Hc containment so the derived representation remains report-scoped, round-trip exact under normalization, benchmark-scope bounded, and unusable as semantic or pipeline authority.

## Scope

- tighten SCIR-Hc semantic-authority and payload-scope checks in the validator
- harden pipeline rejection and report-only SCIR-Hc generation boundaries
- extend the benchmark report schema and generator with explicit SCIR-Hc representation markers plus canonical SCIR-H lineage references
- add negative doctrine tests for pipeline privilege, semantic-authority escalation, round-trip corruption, and schema contamination
- extend the SCIR-Hc failure-mode registry for the new enforced failure classes

## Non-goals

- introducing any new representation, IR, or alternate pipeline
- weakening canonical SCIR-H, lowering, reconstruction, or backend contracts
- removing diagnostic SCIR-H benchmark metrics that already belong to the active benchmark design
- widening SCIR-Hc beyond deterministic derived compression and report surfaces

## Touched files

- `plans/2026-04-03-scirhc-containment-regression-hardening.md`
- `validators/scirhc_validator.py`
- `scripts/scir_bootstrap_pipeline.py`
- `schemas/benchmark_report.schema.json`
- `scripts/benchmark_contract_dry_run.py`
- `reports/examples/benchmark_report.example.json`
- `tests/test_scirhc_doctrine.py`
- `docs/SCIR_HC_FAILURE_MODES.md`
- `BENCHMARK_STRATEGY.md`
- `specs/scir_hc_doctrine.md`

## Invariants that must remain true

- `SCIR-H` remains the only semantic source of truth
- `SCIR-Hc` remains derived only and cannot become semantic input to lowering, reconstruction, backend emission, or canonical validation
- `SCIR-H -> SCIR-Hc -> SCIR-H` remains exact after normalization
- benchmark claim scope remains explicit, single-class, and baseline-qualified
- no enforcement depends on documentation-only convention

## Risks

- benchmark report schema changes can drift from the generator and example artifact
- pipeline hardening can accidentally block existing report-generation paths if the allowed contexts are underspecified
- claim-scope checks can overfit current report payloads unless they are tied to declared metric surfaces and lineage references

## Validation steps

- `python -m py_compile validators/scirhc_validator.py`
- `python -m unittest discover -s tests -p test_scirhc_doctrine.py`
- `python scripts/scir_bootstrap_pipeline.py --mode validate`
- `python scripts/benchmark_contract_dry_run.py`
- `python scripts/benchmark_contract_dry_run.py --claim-run`
- `python scripts/validate_repo_contracts.py --mode validate`
- `python scripts/run_repo_validation.py`

## Rollback strategy

Revert the SCIR-Hc hardening slice together so the validator, schema, benchmark generator/example, pipeline guards, and tests return to the last synchronized state rather than leaving partially enforced containment rules behind.

## Evidence required for completion

- SCIR-Hc semantic-authority escalation is rejected by validator logic and negative tests
- pipeline privilege outside report generation is blocked by code, not convention
- benchmark report schema requires explicit SCIR-Hc representation and canonical lineage references while rejecting contaminated payloads
- all listed validation commands pass

## Completion evidence

- `python -m py_compile validators/scirhc_validator.py scripts/scir_bootstrap_pipeline.py scripts/benchmark_contract_dry_run.py tests/test_scirhc_doctrine.py` passed
- `python -m unittest discover -s tests -p test_scirhc_doctrine.py` passed
- `python scripts/scir_bootstrap_pipeline.py --mode validate` passed
- `python scripts/benchmark_contract_dry_run.py` passed and wrote artifacts under `artifacts/benchmark_runs/python-proof-loop-full-20260403T184850Z`
- `python scripts/benchmark_contract_dry_run.py --claim-run` passed and wrote artifacts under `artifacts/benchmark_runs/python-proof-loop-full-20260403T184850Z`
- `python scripts/validate_repo_contracts.py --mode validate` passed
- `python scripts/run_repo_validation.py` passed
- `python scripts/run_repo_validation.py --require-rust` passed
