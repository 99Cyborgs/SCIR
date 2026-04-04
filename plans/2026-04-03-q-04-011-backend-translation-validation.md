# Backend Translation Validation

Status: complete
Owner: Codex
Date: 2026-04-03

## Objective

Harden execution-backed translation validation for active `SCIR-L -> backend` paths so claim strength, subset admission, comparator semantics, downgrade outcomes, experimental Python coverage, and provenance remain explicit and fail closed under the declared profile and preservation contract.

## Scope

- harden the translation-validation report schema around explicit evidence strength, subset admission, equivalence mode, downgrade reasons, and provenance
- add explicit helper-free Wasm subset classification before backend execution
- refactor translation-validation outcomes away from binary pass/fail into explicit machine-readable outcome classes
- strengthen the comparison engine from nominal equality into structured trace and observation comparison
- add adversarial and mutation-driven validator tests for backend drift and comparator drift
- thread explicit target-profile, equivalence-mode, observable-set, and contract-bounded controls through translation-validation entrypoints
- add a clearly non-default experimental Python translation-validation lane that reuses the same report schema without changing the main reconstruction contract
- update governing docs and decision records so helper-free Wasm subset promotion remains explicit and fail-closed

## Non-goals

- broadening the active backend surface beyond the admitted helper-free Wasm subset
- activating `SCIR-L -> Python` as a new canonical reconstruction path
- introducing external runtime dependencies such as `wasmtime`
- claiming native, host, or whole-language backend parity
- weakening the current `SCIR-H -> SCIR-L` or `SCIR-H -> Python` preservation-report contracts

## Touched files

- runtime/scirl_interpreter.py
- validators/translation_validator.py
- validators/wasm_subset_classifier.py
- scripts/scir_bootstrap_pipeline.py
- scripts/validate_translation.py
- scripts/run_repo_validation.py
- tests/test_translation_validator.py
- tests/test_translation_validator_mutations.py
- tests/fixtures/translation_validation/*
- schemas/translation_validation_report.schema.json
- reports/examples/translation_validation_report.example.json
- VALIDATION_STRATEGY.md
- specs/validator_invariants.md
- DECISION_REGISTER.md

## Invariants that must remain true

- `SCIR-H` remains the only normative semantic source of truth
- `SCIR-L` remains derivative only and may not mint new semantics
- the active Wasm backend stays helper-free, profile `P`, and subset-bound
- importer-only Tier `B` cases remain outside executable backend validation
- opaque and unsafe boundaries remain explicit and capability-accounted
- default validation remains dependency-free and Windows-safe
- helper-free Wasm subset admission must fail closed before execution begins
- the default repository contract must remain Wasm-first; any Python translation-validation lane must remain explicitly experimental and opt-in

## Risks

- overfitting the validator to current emitter shapes instead of the declared bounded contract
- accidentally conflating `H -> L` lowering preservation with `L -> backend` translation validation
- introducing a report/schema surface that drifts from repository contract checks
- creating backend execution assumptions that imply unsupported parity claims
- making downgrade states ambiguous enough that pipeline consumers silently treat them as semantic success
- reporting fake provenance for mismatches that cannot be rooted in existing lowering origins

## Validation steps

- python -m unittest tests.test_translation_validator
- python -m unittest tests.test_translation_validator_mutations
- python -m unittest discover -s tests
- python scripts/validate_translation.py
- python scripts/validate_translation.py --include-experimental-python
- python scripts/scir_bootstrap_pipeline.py --mode validate
- python scripts/scir_bootstrap_pipeline.py --language rust --mode validate
- python scripts/validate_repo_contracts.py --mode validate
- python scripts/run_repo_validation.py

## Rollback strategy

Revert the schema, validator, subset-classifier, pipeline, and test updates together, then restore the prior translation-validation report contract and remove the new downgrade/provenance policy updates from docs and decision records.

## Evidence required for completion

- passing focused translation-validator and mutation unit tests
- passing dedicated translation-validation script for the default Wasm lane
- passing optional experimental Python translation-validation invocation without altering the default gate
- passing Python bootstrap pipeline validation
- passing Rust bootstrap pipeline validation in an environment with Rust
- passing repository contract validation with updated schemas/examples/docs and promotion constraints

## Completion evidence

- `python -m unittest tests.test_translation_validator` passed
- `python -m unittest tests.test_translation_validator_mutations` passed
- `python -m unittest discover -s tests` passed
- `python scripts/validate_translation.py` passed
- `python scripts/validate_translation.py --include-experimental-python` passed
- `python scripts/scir_bootstrap_pipeline.py --mode validate` passed
- `python scripts/scir_bootstrap_pipeline.py --language rust --mode validate` passed
- `python scripts/validate_repo_contracts.py --mode validate` passed
- `python scripts/run_repo_validation.py` passed
