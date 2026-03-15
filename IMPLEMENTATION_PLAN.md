# IMPLEMENTATION_PLAN
Status: Normative

## Purpose

This file fixes staged implementation order. It is optimized for information gain, not breadth.

## Sequencing rule

Do not start a later phase before the previous phase meets its gate, unless `DECISION_REGISTER.md` records an explicit exception.

## Phase plan

| Phase | Objective | Primary files | Exit gate |
| --- | --- | --- | --- |
| 1 | freeze `SCIR-H` core and repository contracts | `specs/scir_h_spec.md`, `specs/type_effect_capability_model.md`, `specs/ownership_alias_model.md`, `specs/provenance_and_stable_id_spec.md`, `specs/validator_invariants.md`, `schemas/*`, `VALIDATION_STRATEGY.md`, `BENCHMARK_STRATEGY.md`, `plans/milestone_01_h_core.md` | canonical `SCIR-H` core is stable enough to seed parser/formatter/validator implementation |
| 2 | Python subset importer | `frontend/python/*`, `docs/feature_tiering.md`, `docs/unsupported_cases.md`, `schemas/module_manifest.schema.json`, `schemas/feature_tier_report.schema.json`, `plans/milestone_02_python_importer.md` | targeted Python subset imports with explicit tiering and validator-ready `SCIR-H` output |
| 3 | `SCIR-L` core and lowering | `specs/scir_l_spec.md`, `specs/concurrency_model.md`, `validators/scir_l/AGENTS.md`, `validators/translation/AGENTS.md`, `plans/milestone_03_l_lowering.md` | validated `H -> L` lowering with no `L`-only semantics |
| 4 | reconstruction pipeline | `docs/reconstruction_policy.md`, `schemas/preservation_report.schema.json`, `schemas/reconstruction_report.schema.json`, `plans/milestone_04_reconstruction.md` | round-trip evidence for the targeted subset with preservation downgrades explicit |
| 5 | benchmark harness | `benchmarks/*`, `schemas/benchmark_manifest.schema.json`, `schemas/benchmark_result.schema.json`, `plans/milestone_05_benchmark_harness.md` | Track A and B run on the targeted subset; Track C harness contract exists |
| 6 | Rust subset and initial optimization | `frontend/rust/*`, `docs/runtime_doctrine.md`, `specs/scir_l_spec.md`, `plans/PLANS.md` | Rust safe subset imports; optimization work is profile-gated and benchmarked |

## Phase details

### Phase 1 — `SCIR-H` core

Required outcomes:

- freeze canonical declaration and type vocabulary,
- freeze stable ID rules,
- freeze hard invariants,
- freeze machine-readable report schemas,
- freeze benchmark doctrine and kill criteria.

Failure mode:

- grammar churn or unresolved core semantics prevent frontend work.

### Phase 2 — Python subset importer

Required outcomes:

- importer scope is explicit,
- unsupported Python features remain explicit,
- feature tier classification is mandatory,
- opaque boundaries are contract-bearing.

Failure mode:

- targeted subset still requires too much Tier `C` or Tier `D`.

### Phase 3 — `SCIR-L` core and lowering

Required outcomes:

- `SCIR-L` stays derivative,
- provenance survives lowering,
- effect and memory sequencing are explicit,
- validator checks SSA, CFG, tokens, and provenance.

Failure mode:

- meaning exists only in `SCIR-L`.

### Phase 4 — reconstruction

Required outcomes:

- reconstruction comes primarily from `SCIR-H`,
- profile `R` and `D` downgrades are explicit,
- compile/test and idiomaticity evidence exist.

Failure mode:

- reconstruction ugliness or failed round-trip dominates.

### Phase 5 — benchmark harness

Required outcomes:

- benchmark manifests are explicit,
- baselines are mandatory,
- contamination controls exist,
- success and kill gates are executable as policy.

Failure mode:

- the program cannot falsify itself.

### Phase 6 — Rust subset and optimization

Required outcomes:

- witness and alias model are exercised by a second language,
- optimization work is profile-gated,
- no optimization claim bypasses benchmark evidence.

Failure mode:

- repository complexity expands faster than information gain.

## Planning trigger

Any change to this sequencing requires:

- a plan in `plans/`,
- a decision register update,
- benchmark impact notes,
- explicit rationale for why the information-gain ordering is changing.
