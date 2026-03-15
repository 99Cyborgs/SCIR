# Milestone 01 — H Core
Status: proposed

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
- `schemas/*`
- `VALIDATION_STRATEGY.md`
- `BENCHMARK_STRATEGY.md`

## Invariants

- `SCIR-H` remains canonical
- no implicit effects or mutation
- no hidden unsupported semantics
- stable ID rules stay deterministic

## Risks

- unresolved exception and concurrency grammar questions
- grammar too large or too small for frontends

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
