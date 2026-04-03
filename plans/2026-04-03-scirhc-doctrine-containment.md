# 2026-04-03 SCIR-Hc Doctrine Containment

Status: complete
Owner: Codex
Date: 2026-04-03

## Objective

Formalize SCIR-Hc governance so the compressed representation remains strictly derivative, deterministically generated, round-trip safe, benchmark-scope bounded, and unusable as a semantic authority or downstream pipeline input.

## Scope

- add a normative SCIR-Hc doctrine addendum with executable validator obligations
- extend the SCIR-Hc model with machine-readable omission provenance
- add a dedicated SCIR-Hc validator module for authority, determinism, hidden-semantics, round-trip, and claim-scope enforcement
- hard-stop any lowering, reconstruction, or backend-emission path that tries to consume SCIR-Hc directly
- constrain benchmark reports with explicit claim-class and evidence-class contracts
- add doctrine-focused tests for forbidden paths and overclaim rejection

## Non-goals

- introducing any new semantic layer or alternate canonical representation
- weakening canonical SCIR-H, SCIR-L, reconstruction, or benchmark falsifiability rules
- widening the active subset, adding speculative compression features, or adding new dependencies
- promoting external context, heuristics, or model-dependent inference into SCIR-Hc derivation

## Touched files

- `plans/2026-04-03-scirhc-doctrine-containment.md`
- `ARCHITECTURE.md`
- `BENCHMARK_STRATEGY.md`
- `DECISION_REGISTER.md`
- `VALIDATION_STRATEGY.md`
- `benchmarks/README.md`
- `benchmarks/success_failure_gates.md`
- `docs/SCIR_HC_FAILURE_MODES.md`
- `docs/scir_h_overview.md`
- `reports/README.md`
- `reports/examples/benchmark_report.example.json`
- `reports/exports/decision_register.export.json`
- `schemas/benchmark_report.schema.json`
- `scripts/benchmark_contract_dry_run.py`
- `scripts/run_repo_validation.py`
- `scripts/scir_bootstrap_pipeline.py`
- `scripts/scir_h_bootstrap_model.py`
- `scripts/validate_repo_contracts.py`
- `specs/scir_h_spec.md`
- `specs/scir_hc_doctrine.md`
- `specs/validator_invariants.md`
- `tests/test_scirhc_doctrine.py`
- `validators/scirhc_validator.py`
- `validators/validator_contracts.md`

## Invariants that must remain true

- `SCIR-H` remains the only semantic source of truth
- `SCIR-Hc` remains derivative only and cannot become valid input to lowering, reconstruction, backend emission, or semantic claim generation
- `SCIR-H -> SCIR-Hc` derivation remains deterministic, idempotent, and context-independent
- `SCIR-Hc -> SCIR-H` round-trip remains mandatory before any downstream use
- benchmark claims remain baseline-qualified, profile-qualified, and must not generalize SCIR-Hc evidence into semantic-preservation claims
- no unsupported witness, capability, or heuristic reconstruction surface becomes active through doctrine hardening

## Risks

- provenance metadata can silently become a second hidden semantics channel if the validator allows unexplained omissions
- compact metadata syntax can inflate SCIR-Hc token counts enough to perturb benchmark thresholds if not kept minimal
- benchmark report schema changes can drift from the claim-run builder or example artifacts
- pipeline guards can be incomplete if only one Python proof-loop entrypoint is hardened

## Validation steps

- `python -m pytest tests/test_scirhc_doctrine.py`
- `python scripts/scir_bootstrap_pipeline.py --mode validate`
- `python scripts/benchmark_contract_dry_run.py`
- `python scripts/benchmark_contract_dry_run.py --claim-run`
- `python scripts/validate_repo_contracts.py --mode validate`

## Rollback strategy

Revert the SCIR-Hc doctrine-containment slice as one unit by removing the dedicated validator, provenance metadata, benchmark claim-class enforcement, and pipeline guard additions together while preserving any purely explanatory text that still matches the pre-containment architecture.

## Evidence required for completion

- the doctrine addendum exists and is reflected in the active validator and benchmark contracts
- SCIR-Hc omissions carry machine-readable provenance and unexplained omissions are rejected
- SCIR-Hc cannot enter lowering, reconstruction, or backend emission paths
- benchmark reports expose claim-class and evidence-class fields and reject cross-class overclaiming
- the listed validation commands pass or any remaining failure is explicit and attributable outside this slice

## Completion evidence

- `python -m py_compile scripts/scir_h_bootstrap_model.py validators/scirhc_validator.py scripts/scir_bootstrap_pipeline.py scripts/benchmark_contract_dry_run.py scripts/run_repo_validation.py scripts/validate_repo_contracts.py tests/test_scirhc_doctrine.py` passed
- `python -m unittest discover -s tests -p test_scirhc_doctrine.py` passed
- `python scripts/scir_bootstrap_pipeline.py --mode validate` passed
- `python scripts/benchmark_contract_dry_run.py` passed and wrote artifacts under `artifacts/benchmark_runs/python-proof-loop-full-20260403T181533Z`
- `python scripts/benchmark_contract_dry_run.py --claim-run` passed and wrote artifacts under `artifacts/benchmark_runs/python-proof-loop-full-20260403T181552Z`
- `python scripts/validate_repo_contracts.py --mode validate` passed
- `python scripts/run_repo_validation.py` passed
