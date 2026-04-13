# Validator negative-path hardening

Status: complete
Owner: Codex
Date: 2026-04-10

## Objective

Harden rejection coverage for the active Python-first MVP validator lane without widening `SCIR-H`, `SCIR-L`, profiles, or feature tiers.

## Scope

- add invalid `SCIR-H` fixtures for ambiguous top-level names and opaque-value projection
- add invalid `SCIR-L` fixtures for terminator-level lowering-rule drift and unsupported terminator kinds
- tighten bootstrap self-tests for missing downgrade evidence on opaque translation, opaque reconstruction, and Wasm preservation reports
- update the active plan surface so `CURRENT_FOCUS.md` and repository-contract validation point at this item

## Non-goals

- grammar widening
- backend widening
- benchmark-track redesign
- new validator entrypoints or top-level commands

## Touched files

- CURRENT_FOCUS.md
- plans/2026-04-10-validator-negative-path-hardening.md
- scripts/scir_bootstrap_pipeline.py
- scripts/validate_repo_contracts.py
- VALIDATION_STRATEGY.md
- validators/validator_contracts.md
- tests/invalid_scir_h/manifest.json
- tests/invalid_scir_l/manifest.json

## Invariants that must remain true

- `SCIR-H` remains the only normative semantic authority
- `SCIR-L` remains derivative-only
- negative-path expansion must not widen the admitted executable subset
- repository contract, importer conformance, and bootstrap pipeline remain the existing blocking surfaces

## Risks

- adding negative fixtures that parse but accidentally exercise unsupported semantics instead of the intended invariant
- tightening preservation checks more than the active opaque-boundary doctrine permits
- drifting manifest hashes while expanding negative corpora

## Validation steps

- `python scripts/validate_repo_contracts.py --mode test`
- `python scripts/python_importer_conformance.py --mode test`
- `python scripts/scir_bootstrap_pipeline.py --mode test`
- `python scripts/run_repo_validation.py`

## Rollback strategy

Revert only the new negative fixtures or stricter self-test assertions that prove inconsistent with the existing normative doctrine, while keeping the active-plan surface on the validator-hardening item.

## Evidence required for completion

- passing negative-path validation commands
- manifest-backed invalid fixture coverage for the new `SCIR-H` and `SCIR-L` rejection cases
- diff review confirming no grammar, backend, profile, or command-surface widening

## Completion evidence

- `python scripts/validate_repo_contracts.py --mode test`
- `python scripts/python_importer_conformance.py --mode test`
- `python scripts/scir_bootstrap_pipeline.py --mode test`
- `python scripts/run_repo_validation.py`
- added invalid-fixture coverage for ambiguous top-level names, opaque-value projection, missing terminator lowering rules, and unsupported terminator kinds
- diff review outcome: validator hardening only; no widened grammar, backend, profile, tier, or command surface
