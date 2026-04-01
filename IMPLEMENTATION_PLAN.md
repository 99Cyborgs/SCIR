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
| 6A | Rust safe-subset importer and round-trip evidence | `frontend/rust/*`, `tests/rust_importer/*`, `scripts/scir_rust_bootstrap.py`, `scripts/scir_bootstrap_pipeline.py`, `specs/scir_h_spec.md`, `specs/scir_l_spec.md`, `docs/runtime_doctrine.md`, `plans/milestone_06a_rust_subset.md` | Rust safe subset imports; Tier `A` cases round-trip through `SCIR-H -> SCIR-L -> Rust`; unsafe boundaries stay explicit |
| 6B | initial optimization and Track `D` activation | `docs/runtime_doctrine.md`, `docs/target_profiles.md`, `specs/scir_l_spec.md`, `schemas/*`, `benchmarks/*`, `scripts/scir_bootstrap_pipeline.py`, `plans/milestone_06b_dual_track_d_activation.md` | profile-gated optimization is benchmarked on fixed Rust `N` and Python `D-PY` slices; `D-JS` remains doctrine-only; witness-bearing second-language execution stays explicitly deferred |
| 7 | witness-bearing second-language evidence | `frontend/typescript/*`, `specs/type_effect_capability_model.md`, `VALIDATION_STRATEGY.md`, `validators/validator_contracts.md`, `plans/milestone_07_typescript_witness_slice.md` | TypeScript interface-shaped witness imports are validator- and report-covered; translation validation enforces provenance continuity and profile-qualified downgrades; `D-JS` remains non-executable unless a later plan explicitly widens downstream contracts |

## Post-6B roadmap note

The historical Phase 1-6B sequence remains complete and accepted, and Milestone 02B is now complete as the bounded Python semantic expansion milestone. Its admitted follow-on cases remain fixture-backed, tier-explicit, and importer-only unless a later milestone widens executable lowering, reconstruction, or benchmark scope explicitly.

Phase 7 is now the active new architecture phase after 6B and after the completed Milestone 02B closeout. Its default candidate slice remains TypeScript interface-shaped witness evidence before any Rust trait/impl execution work or broader backend/runtime expansion, and it stays planning-only and non-executable until later downstream contracts are published.

## Phase details

### Phase 1 - `SCIR-H` core

Required outcomes:

- freeze canonical declaration and type vocabulary,
- freeze stable ID rules,
- freeze hard invariants,
- freeze machine-readable report schemas,
- freeze benchmark doctrine and kill criteria.

Failure mode:

- grammar churn or unresolved core semantics prevent frontend work.

### Phase 2 - Python subset importer

Required outcomes:

- importer scope is explicit,
- unsupported Python features remain explicit,
- feature tier classification is mandatory,
- opaque boundaries are contract-bearing.

Failure mode:

- targeted subset still requires too much Tier `C` or Tier `D`.

### Phase 3 - `SCIR-L` core and lowering

Required outcomes:

- `SCIR-L` stays derivative,
- provenance survives lowering,
- effect and memory sequencing are explicit,
- validator checks SSA, CFG, tokens, and provenance.

Failure mode:

- meaning exists only in `SCIR-L`.

### Phase 4 - reconstruction

Required outcomes:

- reconstruction comes primarily from `SCIR-H`,
- profile `R` and `D-PY` downgrades are explicit,
- compile/test and idiomaticity evidence exist.

Failure mode:

- reconstruction ugliness or failed round-trip dominates.

### Phase 5 - benchmark harness

Required outcomes:

- benchmark manifests are explicit,
- baselines are mandatory,
- contamination controls exist,
- success and kill gates are executable as policy.

Failure mode:

- the program cannot falsify itself.

### Phase 6A - Rust safe subset

Required outcomes:

- a fixed Rust bootstrap corpus exists,
- the Rust importer emits canonical `SCIR-H`,
- the Rust slice exercises borrowed-record field places,
- supported Rust Tier `A` cases round-trip through reconstruction with compile/test evidence,
- explicit unsafe boundaries remain Tier `C`.

Failure mode:

- the Rust toolchain is absent or the safe subset still requires too much opaque fallback.

### Phase 6B - optimization

Required outcomes:

- Rust alias-sensitive and Python host-sensitive fixed slices emit executable Track `D` evidence,
- optimization work is profile-gated,
- monolithic profile `D` is superseded by `D-PY` and `D-JS`,
- witness-bearing second-language execution remains explicitly deferred to a later milestone,
- no optimization claim bypasses benchmark evidence.

Failure mode:

- repository complexity expands faster than information gain.

### Phase 7 - witness-bearing second-language evidence

Required outcomes:

- Milestone 02B is complete before broader frontend scope grows again,
- TypeScript interface-shaped witness import is explicit as the first witness-bearing second-language slice,
- witness semantics stay explicit in `SCIR-H` and do not migrate into `SCIR-L`-only meaning,
- translation validation blocks on `H -> L` provenance continuity, profile-qualified downgrade reporting, and no optimizer-only facts flowing back into `SCIR-H`,
- `D-JS` remains doctrine-only unless a later plan explicitly adds executable lowering, reconstruction, and benchmark gates,
- no new native backend track is introduced as part of this phase.

Failure mode:

- witness-bearing work broadens host/runtime claims faster than validator, preservation, and benchmark doctrine can justify.

## Planning trigger

Any change to this sequencing requires:

- a plan in `plans/`,
- a decision register update,
- benchmark impact notes,
- explicit rationale for why the information-gain ordering is changing.
