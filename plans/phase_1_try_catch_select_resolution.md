# Phase 1 Try Catch and Select Resolution

Status: complete
Owner: Codex
Date: 2026-03-15

## Objective

Resolve the remaining Phase 1 blocker questions by adding minimal canonical `try/catch` and `select` forms to `SCIR-H`, then synchronize the validator, architecture, assumptions, and milestone surfaces around those decisions.

## Scope

- add minimal structured `try/catch` to `specs/scir_h_spec.md`
- add minimal channel `select` to `specs/scir_h_spec.md`
- update the type/effect and concurrency contracts for those forms
- update validator-facing and explanatory docs so they reject richer unsupported variants
- resolve `OQ-008` and `OQ-009`
- record the decisions in `DECISION_REGISTER.md`
- close or explicitly hand off Milestone 01

## Non-goals

- redesigning `SCIR-L`
- adding lowering details beyond deferring them to Phase 3
- changing target profiles, preservation levels, feature tiers, or benchmark doctrine
- starting importer work or Phase 2 planning beyond the handoff note

## Touched files

- `plans/phase_1_try_catch_select_resolution.md`
- `specs/scir_h_spec.md`
- `specs/type_effect_capability_model.md`
- `specs/concurrency_model.md`
- `specs/validator_invariants.md`
- `validators/validator_contracts.md`
- `VALIDATION_STRATEGY.md`
- `docs/scir_h_overview.md`
- `ARCHITECTURE.md`
- `OPEN_QUESTIONS.md`
- `ASSUMPTIONS.md`
- `DECISION_REGISTER.md`
- `reports/exports/decision_register.export.json`
- `reports/exports/open_questions.export.json`
- `plans/milestone_01_h_core.md`

## Invariants that must remain true

- `SCIR-H` remains the only canonical semantic source of truth
- `SCIR-L` remains derivative and gains no new independent semantics in this slice
- no hidden control transfer, implicit effects, or implicit concurrency semantics are introduced
- richer exception and selection forms remain explicitly unsupported in canonical v0.1
- `make validate` and `make benchmark` remain the top-level command contracts

## Risks

- adding too much syntax around `select` could quietly broaden the canonical surface
- exception handling wording could accidentally imply a subtyping or `finally` model that the repo does not define
- touched specs and docs could drift if the blocker resolution is not applied consistently across all required surfaces

## Validation steps

- `python scripts/validate_repo_contracts.py --mode validate`
- `python scripts/validate_repo_contracts.py --mode test`
- `python scripts/benchmark_contract_dry_run.py`

## Rollback strategy

Revert the semantic additions, restore `OQ-008` and `OQ-009` as blockers, and keep the smaller `SCIR-H` core until a narrower or better-specified resolution is chosen.

## Evidence required for completion

- `specs/scir_h_spec.md` includes the minimal canonical `try/catch` and `select` forms
- validator-facing docs reject richer unsupported forms
- `OPEN_QUESTIONS.md`, `ASSUMPTIONS.md`, and `DECISION_REGISTER.md` agree on the resolved state
- `plans/milestone_01_h_core.md` records the Phase 1 outcome and next-week handoff
- validate, test, and benchmark dry-run pass after the change

## Completion evidence

- `OQ-008` and `OQ-009` were resolved by adding minimal canonical `try/catch` and channel `select` forms to `SCIR-H`
- validator-facing docs now reject `finally`, multi-catch, non-channel `select` arms, and default/timeout/priority semantics
- `python scripts/validate_repo_contracts.py --mode validate` passed on 2026-03-15
- `python scripts/validate_repo_contracts.py --mode test` passed on 2026-03-15
- `python scripts/benchmark_contract_dry_run.py` passed on 2026-03-15
