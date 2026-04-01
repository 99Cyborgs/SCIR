# Milestone 01 — H Core
Status: complete

## Objective

Freeze the minimum credible `SCIR-H` core and the repository contracts needed to implement parser, formatter, validator, and report generation.

## Scope

- `SCIR-H` grammar and canonical formatting
- type/effect/capability model
- ownership and alias model
- stable IDs and provenance
- validator invariants
- report schemas
- benchmark doctrine skeleton

## Non-goals

- executable parser implementation
- lowering
- backend work
- whole-language importers

## Touched files

- `specs/scir_h_spec.md`
- `specs/type_effect_capability_model.md`
- `specs/ownership_alias_model.md`
- `specs/provenance_and_stable_id_spec.md`
- `specs/validator_invariants.md`
- `specs/concurrency_model.md`
- `docs/scir_h_overview.md`
- `ARCHITECTURE.md`
- `validators/validator_contracts.md`
- `schemas/*`
- `VALIDATION_STRATEGY.md`
- `BENCHMARK_STRATEGY.md`
- `OPEN_QUESTIONS.md`
- `ASSUMPTIONS.md`
- `DECISION_REGISTER.md`

## Invariants

- `SCIR-H` remains canonical
- no implicit effects or mutation
- no hidden unsupported semantics
- stable ID rules stay deterministic

## Risks

- minimal `try/catch` and `select` forms may still prove too narrow for some frontends
- `SCIR-L` lowering details for these forms remain a Phase 3 concern

## Validation steps

```bash
make validate
make benchmark
```

## Rollback strategy

Revert the last semantic expansion, record the issue in `OPEN_QUESTIONS.md`, and keep the smaller core.

## Evidence required for completion

- stable `SCIR-H` grammar text
- complete validator invariant table
- parseable JSON schemas
- updated decision register if core doctrine changes

## Completion evidence

- `specs/scir_h_spec.md` now includes minimal canonical `try/catch` and channel `select`
- `OQ-008` and `OQ-009` are resolved and removed from `OPEN_QUESTIONS.md`
- `ASSUMPTIONS.md` and `DECISION_REGISTER.md` reflect the resolved v0.1 forms
- `python scripts/validate_repo_contracts.py --mode validate` passed on 2026-03-15
- `python scripts/validate_repo_contracts.py --mode test` passed on 2026-03-15
- `python scripts/benchmark_contract_dry_run.py` passed on 2026-03-15

## Handoff note

Phase 1 closed; Python importer planning can begin next week.
