# AGENTS.md
Status: Normative

## Project overview

SCIR is a two-layer semantic compression substrate.

- `SCIR-H`: canonical high-level semantics for inspection, stable transformation, AI generation, and reconstruction.
- `SCIR-L`: lowered control/dataflow form for analysis, optimization, and backend preparation.

First build target:

- `SCIR-H` core
- parser/formatter contract
- `SCIR-H` validator
- stable ID and provenance model
- benchmark harness skeleton

Not first build target:

- a new mass-market user language
- broad whole-language C++ support
- proof-heavy backend verification before operational validator value exists
- backend sprawl

## Source authority order

Use this order when files disagree:

1. `specs/`
2. `schemas/`
3. repository structure and current code
4. `benchmarks/`
5. notes and plans

Do not silently merge incompatible semantics. Record unresolved conflicts in `OPEN_QUESTIONS.md`.

## Read first

Always read these before coding:

1. `SYSTEM_BOUNDARY.md`
2. `ARCHITECTURE.md`
3. `specs/scir_h_spec.md`
4. `specs/scir_l_spec.md`
5. `specs/type_effect_capability_model.md`
6. `specs/ownership_alias_model.md`
7. `specs/interop_and_opaque_boundary_spec.md`
8. `specs/validator_invariants.md`
9. `docs/target_profiles.md`
10. `docs/preservation_contract.md`
11. `docs/feature_tiering.md`
12. `VALIDATION_STRATEGY.md`
13. `BENCHMARK_STRATEGY.md`

Read the nearest local `AGENTS.md` before editing inside a subtree.

## Commands

Use the repository root.

```bash
make build
make lint
make test
make validate
make benchmark
make ci
```

Do not replace these commands without updating `README.md`, this file, CI workflows, and `ci/*.md`.

## When you must consult `IMPLEMENTATION_PLAN.md`

Consult it before:

- starting any milestone work,
- changing phase ordering,
- adding a new frontend, backend, validator, or benchmark track,
- expanding scope beyond the current credible build path,
- modifying a file listed in a milestone seed document.

## When you must consult `plans/PLANS.md`

Create or update a plan before work that:

- touches 3 or more files,
- touches both `specs/` and another subtree,
- changes schemas,
- changes validator behavior,
- changes preservation levels, target profiles, or feature tiers,
- changes unsupported-case handling,
- changes benchmark manifests, gates, or baselines,
- introduces a new directory or tool contract.

Use the exact plan template in `plans/PLANS.md`.

## Hard constraints

- Do not invent unsupported semantics.
- Do not downgrade explicit unsupported cases into implicit support.
- Do not move semantics from `SCIR-H` into `SCIR-L` only.
- Do not claim preservation without a profile and a preservation level.
- Do not claim support for a feature without a tier.
- Do not hide unsafe, foreign, host, or opaque boundaries.
- Do not compare SCIR only to weak baselines.
- Do not broaden scope to full-language fidelity claims.
- Do not merge architecture changes without updating the decision register.

## Change discipline

Every architecture-affecting change must update the relevant set of files.

- `SCIR-H` semantics change:
  - `specs/scir_h_spec.md`
  - `docs/scir_h_overview.md`
  - `ARCHITECTURE.md`
  - `validators/validator_contracts.md`
  - `specs/validator_invariants.md`
  - `VALIDATION_STRATEGY.md`
  - `DECISION_REGISTER.md`
- `SCIR-L` semantics change:
  - `specs/scir_l_spec.md`
  - `docs/scir_l_overview.md`
  - `ARCHITECTURE.md`
  - `validators/validator_contracts.md`
  - `specs/validator_invariants.md`
  - `VALIDATION_STRATEGY.md`
  - `DECISION_REGISTER.md`
- target profiles or preservation change:
  - `docs/target_profiles.md`
  - `docs/preservation_contract.md`
  - `BENCHMARK_STRATEGY.md`
  - `benchmarks/success_failure_gates.md`
  - `DECISION_REGISTER.md`
- feature tier or unsupported-case change:
  - `docs/feature_tiering.md`
  - `docs/unsupported_cases.md`
  - relevant `frontend/*/IMPORT_SCOPE.md`
  - `BENCHMARK_STRATEGY.md`
  - `OPEN_QUESTIONS.md` if unresolved
- schema change:
  - changed file in `schemas/`
  - any markdown file that defines or consumes the schema
  - `VALIDATION_STRATEGY.md` or `BENCHMARK_STRATEGY.md`
  - CI if validation behavior changes

## Definition of done

A task is done only when all are true:

1. touched specs and docs agree,
2. local `AGENTS.md` rules were followed,
3. preservation/profile/tier implications are explicit,
4. unsupported and opaque cases are explicit,
5. required schemas or report contracts are updated,
6. `make validate` passes,
7. `make benchmark` still passes for doctrine-level changes,
8. `DECISION_REGISTER.md` is updated if architecture changed,
9. `OPEN_QUESTIONS.md` is updated if ambiguity remains,
10. completion evidence is recorded in the active plan.

## Default operating posture

Prefer the narrow credible path:

- Python subset importer first
- `SCIR-H` validator before optimization work
- `H -> L` before backend sprawl
- reconstruction before mass-market syntax work
- benchmark harness before AI claims
- Rust subset after Python subset proves useful

## Canonical labels

Preservation labels: `P0`, `P1`, `P2`, `P3`, `PX`.
Feature tiers: `Tier A`, `Tier B`, `Tier C`, `Tier D`.
