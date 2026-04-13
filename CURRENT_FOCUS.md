# CURRENT_FOCUS
Status: Active

## Active target

Python subset importer -> canonical `SCIR-H` -> validator hardening.

## Boundaries

- Keep `SCIR-H` as the only normative semantic authority.
- Keep `SCIR-L` derivative-only and unchanged unless validator hardening requires a spec-first correction.
- Treat the current 11-case Python executable proof loop as the completed, frozen MVP corpus for this phase.
- Do not widen grammar, Python scope, or backend scope during this item.
- Keep Rust importer-first, helper-free Wasm bounded, and Track `C` non-default as maintained but frozen support lanes.
- Require a new plan plus a new decision-register update before any future proof-loop widening or support-lane promotion.
- Keep release-bundle machinery opt-in only.

## This item

- replace the completed Wasm boundary-lock slice with a post-proof-loop consolidation item focused on validator hardening, contract honesty, freeze enforcement, and explicit Track `C` boundary locking
- keep repository contract, importer conformance, benchmark doctrine, backend doctrine, and roadmap surfaces aligned to the frozen 11-case Python proof loop
- keep bounded Rust importer evidence, helper-free Wasm, and the retained Track `C` pilot synchronized without promoting them into active scope
- resolve the remaining Track `C` sequencing ambiguity in favor of retained non-default MVP support only
- make future Python proof-loop changes, helper-free Wasm widening or backend activation, Rust round-trip activation, or Track `C` promotion require fresh decision and plan updates

## Done when

- `README.md`, `ARCHITECTURE.md`, and this file name the same active target
- `CURRENT_FOCUS.md` no longer points to the completed Wasm boundary-lock slice
- `BENCHMARK_STRATEGY.md`, `benchmarks/tracks.md`, and `scripts/benchmark_contract_metadata.py` describe the same retained non-default Track `C` posture
- `scripts/validate_repo_contracts.py` blocks frozen proof-loop case-set drift, Python importer-only reintroduction, and silent Rust/Wasm/Track `C` promotion
- retained Track `C` sample artifacts and doctrine remain synchronized to the frozen executable proof-loop case set
- `python scripts/run_repo_validation.py` passes with Rust, Wasm, and Track `C` retained as support lanes only
- completion evidence is recorded in the active plan

## Plan

- `plans/2026-04-12-track-c-mvp-boundary-lock-and-phase-6-reset.md`
