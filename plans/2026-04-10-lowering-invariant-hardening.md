# Lowering invariant hardening

Status: complete
Owner: Codex
Date: 2026-04-10

## Objective

Tighten `SCIR-H -> SCIR-L` invariant enforcement for the admitted bootstrap cases without widening the lowering subset, profiles, or backend claims.

## Scope

- strengthen case-specific lowering-alignment checks for admitted Python and Rust proof-loop cases
- require exact translation-report observables, evidence, and downgrade accounting for the admitted `h_to_l` paths
- extend pipeline self-tests so lowering-shape or translation-report drift fails even when generic `SCIR-L` structural validation still passes
- update the active-plan and validator-contract docs to reflect fixed-lowering enforcement

## Non-goals

- grammar widening
- new lowering rules or `SCIR-L` ops
- benchmark-track redesign
- Rust promotion into the active proof loop

## Touched files

- CURRENT_FOCUS.md
- LOWERING_CONTRACT.md
- VALIDATION_STRATEGY.md
- validators/validator_contracts.md
- scripts/scir_bootstrap_pipeline.py
- scripts/validate_repo_contracts.py
- plans/2026-04-10-lowering-invariant-hardening.md

## Invariants that must remain true

- `SCIR-H` remains the only normative semantic authority
- `SCIR-L` remains derivative-only
- the admitted bootstrap lowering subset does not widen
- opaque and unsafe boundary accounting remains explicit and bounded

## Risks

- overfitting alignment checks to incidental formatting instead of semantic bootstrap shape
- tightening translation expectations in ways that conflict with bounded opaque or unsafe handling
- drifting the active-plan surface if the new dated plan is not kept synchronized

## Validation steps

- `python scripts/validate_repo_contracts.py --mode test`
- `python scripts/scir_bootstrap_pipeline.py --mode test`
- `python scripts/run_repo_validation.py`
- `python scripts/run_repo_validation.py --require-rust`

## Rollback strategy

Revert only the exact-shape alignment assertions or translation-report strictness that prove inconsistent with the established lowering contract, while preserving the active-plan linkage.

## Evidence required for completion

- passing lowering-focused validation commands
- self-tests proving exact lowering-shape and translation-report drift are rejected
- diff review confirming no new lowering rules, ops, profiles, or backend claims were introduced

## Completion evidence

- `python scripts/validate_repo_contracts.py --mode test`
- `python scripts/scir_bootstrap_pipeline.py --mode test`
- `python scripts/run_repo_validation.py`
- `python scripts/run_repo_validation.py --require-rust`
- self-tests now reject exact lowering-origin drift, exact lowered-call-target drift, Python translation observable/evidence drift, and Rust translation observable drift
- diff review outcome: tightened fixed-lowering enforcement only; no new lowering rules, ops, profiles, or backend claims introduced
