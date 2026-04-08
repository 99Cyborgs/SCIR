---
name: scir-spec-sync
description: Synchronize SCIR normative and consuming surfaces when work changes semantics, schemas, validator doctrine, preservation doctrine, benchmark doctrine, architecture contracts, or other repo-governed claims. Use when Codex must compute the required companion-file update set, preserve source-authority order, and prevent partial doctrine edits.
---

# SCIR Spec Sync

## Goal

Keep authoritative SCIR surfaces synchronized so one bounded change does not leave stale contracts behind.

## Required context

Read the root `AGENTS.md` read order first.
Treat source authority in this order: `specs/`, `schemas/`, repository structure and current code, `benchmarks/`, then notes and plans.
Read the nearest local `AGENTS.md` before editing inside a subtree.

## Workflow

1. Classify the change before editing anything:
   - `SCIR-H` semantics
   - `SCIR-L` semantics
   - schema or report contract
   - target profile or preservation doctrine
   - feature tier or unsupported-case handling
   - benchmark doctrine
   - architecture or decision posture
2. Map the required companion updates from the root `AGENTS.md` change-discipline section.
3. Edit the most authoritative surface first, then every consumer of that surface.
4. Search for stale references in docs, validator contracts, reports, examples, and plans with `rg`.
5. If two authoritative files disagree, stop and record the ambiguity in `OPEN_QUESTIONS.md` instead of silently blending semantics.
6. If the change is architecture-affecting, require `DECISION_REGISTER.md` updates before calling the work complete.
7. Select the smallest sufficient validation gate after the sync map is complete.

## Mandatory sync map

- `SCIR-H` semantics: update `specs/scir_h_spec.md`, `docs/scir_h_overview.md`, `ARCHITECTURE.md`, `validators/validator_contracts.md`, `specs/validator_invariants.md`, `VALIDATION_STRATEGY.md`, and `DECISION_REGISTER.md`.
- `SCIR-L` semantics: update `specs/scir_l_spec.md`, `docs/scir_l_overview.md`, `ARCHITECTURE.md`, `validators/validator_contracts.md`, `specs/validator_invariants.md`, `VALIDATION_STRATEGY.md`, and `DECISION_REGISTER.md`.
- target profiles or preservation: update `docs/target_profiles.md`, `docs/preservation_contract.md`, `BENCHMARK_STRATEGY.md`, `benchmarks/success_failure_gates.md`, and `DECISION_REGISTER.md`.
- feature tiers or unsupported handling: update `docs/feature_tiering.md`, `docs/unsupported_cases.md`, relevant `frontend/*/IMPORT_SCOPE.md`, `BENCHMARK_STRATEGY.md`, and `OPEN_QUESTIONS.md` when ambiguity remains.
- schema changes: update the changed file under `schemas/`, every markdown consumer of that schema, and `VALIDATION_STRATEGY.md` or `BENCHMARK_STRATEGY.md` when validation behavior changes.

## Output contract

Always return:
1. `Change Class`
2. `Authoritative Files`
3. `Consumer Files`
4. `Required Validation`
5. `Open Questions / Decision Updates`

## Hard invariants

- Do not edit explanatory docs while leaving the normative source unchanged.
- Do not hide a required companion update behind "follow-up" language.
- Do not widen scope through benchmark, backend, or importer wording alone.
- Do not mark work complete while a required decision-register or open-question update is still pending.
