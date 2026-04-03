# MVP_SCOPE
Status: Normative

## Goal

This file records the exact subsystem classification for the narrowed SCIR MVP.

## Classification legend

- `keep as core MVP`
- `keep but narrow`
- `defer`
- `archive`
- `delete`
- `missing and required`

## Exact path audit

| Path | Classification | Notes |
| --- | --- | --- |
| `/README.md` | keep but narrow | root contract now matches the implemented MVP only |
| `/SYSTEM_BOUNDARY.md` | keep as core MVP | active scope boundary |
| `/ARCHITECTURE.md` | keep as core MVP | root normative architecture |
| `/IMPLEMENTATION_PLAN.md` | keep as core MVP | rewritten around MVP phases only |
| `/VALIDATION_STRATEGY.md` | keep as core MVP | active validation contract |
| `/BENCHMARK_STRATEGY.md` | keep as core MVP | active benchmark contract |
| `/MVP_SCOPE.md` | keep as core MVP | exact audit table |
| `/ROADMAP.md` | keep as core MVP | active roadmap |
| `/UNSUPPORTED_CASES.md` | keep as core MVP | operator-facing unsupported boundary |
| `/DEFERRED_COMPONENTS.md` | keep as core MVP | explicit non-MVP surfaces |
| `/LOWERING_CONTRACT.md` | keep as core MVP | H-to-L derivative contract |
| `/IDENTITY_MODEL.md` | keep as core MVP | identity and canonical/view split |
| `/SPEC_COMPLETENESS_CHECKLIST.md` | keep as core MVP | construct-by-construct coherence matrix |
| `/specs/scir_h_spec.md` | keep as core MVP | only normative semantic source |
| `/specs/scir_l_spec.md` | keep but narrow | derivative-only lowering subset |
| `/specs/type_effect_capability_model.md` | keep but narrow | capabilities and witness claims reduced to the active subset plus deferred notes |
| `/specs/ownership_alias_model.md` | keep but narrow | narrowed to Python and Rust subset semantics |
| `/specs/interop_and_opaque_boundary_spec.md` | keep but narrow | active opaque and unsafe boundary forms only |
| `/specs/validator_invariants.md` | keep as core MVP | active validator contract |
| `/specs/provenance_and_stable_id_spec.md` | keep but narrow | superseded by `IDENTITY_MODEL.md` where needed |
| `/specs/concurrency_model.md` | defer | only minimal async/await remains active; channel/select work is deferred |
| `/docs/project_overview.md` | keep but narrow | explanatory overview only |
| `/docs/scir_h_overview.md` | keep as core MVP | explanatory H overview |
| `/docs/scir_l_overview.md` | keep as core MVP | explanatory L overview |
| `/docs/reconstruction_policy.md` | keep as core MVP | Python reconstruction policy |
| `/docs/runtime_doctrine.md` | keep but narrow | Wasm `P` profile first; native and `D-JS` deferred |
| `/docs/target_profiles.md` | keep but narrow | active vs deferred profiles explicit |
| `/docs/preservation_contract.md` | keep as core MVP | simplified preservation reporting contract |
| `/docs/feature_tiering.md` | keep as core MVP | active tier policy |
| `/docs/unsupported_cases.md` | keep as core MVP | detailed unsupported-case doctrine |
| `/docs/repository_map.md` | keep as core MVP | detailed path map |
| `/grammar/` | missing and required | no standalone grammar directory exists; active grammar authority is `specs/scir_h_spec.md`, `specs/scir_l_spec.md`, and `scripts/scir_h_bootstrap_model.py` |
| `/parser/` | missing and required | no standalone parser package exists; active parser lives in `scripts/scir_h_bootstrap_model.py` |
| `/formatter/` | missing and required | no standalone formatter package exists; active formatter lives in `scripts/scir_h_bootstrap_model.py` |
| `/scripts/scir_h_bootstrap_model.py` | keep as core MVP | executable parser, formatter, canonicalizer, identity helpers, and view renderer |
| `/scripts/scir_python_bootstrap.py` | keep as core MVP | Python subset importer |
| `/scripts/scir_rust_bootstrap.py` | keep as core MVP | Rust safe-subset importer |
| `/scripts/scir_bootstrap_pipeline.py` | keep but narrow | Python proof loop plus derivative checks; non-MVP benchmark/runtime work is no longer part of the active gate |
| `/scripts/validate_repo_contracts.py` | keep as core MVP | repo contract and checklist validator |
| `/scripts/run_repo_validation.py` | keep as core MVP | top-level MVP validation runner |
| `/scripts/benchmark_contract_dry_run.py` | keep but narrow | Track `A` / `B` only |
| `/scripts/typescript_importer_conformance.py` | defer | retained on disk as a deferred surface only |
| `/frontend/python/IMPORT_SCOPE.md` | keep as core MVP | active frontend scope |
| `/frontend/rust/IMPORT_SCOPE.md` | keep as core MVP | active frontend scope |
| `/frontend/typescript/IMPORT_SCOPE.md` | defer | explicit non-MVP placeholder only |
| `/validators/validator_contracts.md` | keep as core MVP | active validator stack contract |
| `/validators/README.md` | keep as core MVP | validator scope overview |
| `/backends/` | keep as core MVP | active backend contract root |
| `/backends/wasm/README.md` | keep as core MVP | Wasm reference backend MVP contract |
| `/runtime/` | missing and required | no separate runtime directory exists yet; MVP forbids hidden runtime semantics and only allows explicit helper shims when the Wasm contract requires them |
| `/benchmarks/README.md` | keep as core MVP | benchmark doctrine overview |
| `/benchmarks/tracks.md` | keep as core MVP | Track `A` and `B` active, `C` pilot conditional, `D` deferred |
| `/benchmarks/baselines.md` | keep as core MVP | strong-baseline rule |
| `/benchmarks/corpora_policy.md` | keep as core MVP | fixed Python proof-loop corpus plus deferred expansion rules |
| `/benchmarks/contamination_controls.md` | keep as core MVP | contamination-control minimum |
| `/benchmarks/success_failure_gates.md` | keep as core MVP | active success and kill thresholds |
| `/tests/python_importer/cases/` | keep as core MVP | active fixture corpus |
| `/tests/rust_importer/cases/` | keep but narrow | active importer-only Rust corpus |
| `/tests/typescript_importer/` | archive | retained as a dormant placeholder corpus, excluded from active validation |
| `/tests/invalid_scir_h/` | keep as core MVP | seeded invalid canonical examples |
| `/tooling/checker_contract.md` | keep as core MVP | checker remains active |
| `/tooling/formatter_contract.md` | keep as core MVP | formatter remains active |
| `/tooling/explorer_contract.md` | defer | optional low-burden surface only |
| `/tooling/agent_api.md` | defer | explicit non-MVP tooling surface |
| `/ci/validation_pipeline.md` | keep as core MVP | active validation pipeline |
| `/ci/benchmark_pipeline.md` | keep as core MVP | active benchmark pipeline |
| `/ci/release_requirements.md` | keep but narrow | release gate documentation |
| `/.github/workflows/validate.yml` | keep as core MVP | active CI validation job |
| `/.github/workflows/benchmarks.yml` | keep as core MVP | active CI benchmark job |

## Active system rule

If a path is not classified `keep as core MVP` or `keep but narrow`, it must not appear as an active implementation commitment in root docs, validation gates, or benchmark claims.
