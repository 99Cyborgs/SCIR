# CURRENT_FOCUS
Status: Active

## Active target

Frozen 11-case Python proof-loop strong-baseline falsification for Track `A` and Track `B`.

## Current bounded MVP kept comparison-ready

- canonical `SCIR-H`
- derived `SCIR-Hc`
- derivative `SCIR-L`
- validator coverage for `SCIR-H`, `SCIR-Hc`, `SCIR-L`, and `SCIR-H -> SCIR-L` preservation
- Python subset import on the frozen 11-case proof loop
- Python reconstruction from validated `SCIR-H`
- bounded Rust importer-first evidence
- bounded helper-free Wasm validation for the admitted subset
- Track `A` and Track `B` benchmark harnesses

## Boundaries

- Keep `SCIR-H` as the only normative semantic authority.
- Keep `SCIR-L` derivative-only and unchanged unless validator hardening requires a spec-first correction.
- Treat the current 11-case Python executable proof loop as the completed, frozen MVP corpus for this phase.
- Do not widen grammar, Python scope, or backend scope during this item.
- Keep Rust importer-first, helper-free Wasm bounded, and Track `C` non-default as maintained but frozen support lanes.
- Require a new plan plus a new decision-register update before any future proof-loop widening or support-lane promotion.
- Keep release-bundle machinery opt-in only.

## This item

- make the mandatory direct-source and typed-AST baselines real, fair, and executable on the frozen 11-case Python proof-loop corpus
- turn Track `A` and Track `B` into a decision-grade falsification phase with explicit strongest-baseline attribution on every active claim surface
- make the repository classify active results as `SCIR_NECESSARY`, `SCIR_USEFUL_BUT_UNNECESSARY`, `SCIR_NOT_JUSTIFIED`, or `INCONCLUSIVE`
- keep benchmark artifacts, schemas, contamination controls, and reproducibility blocks synchronized to the actual executable run
- keep bounded Rust importer evidence, helper-free Wasm, and the retained Track `C` pilot synchronized without promoting them into active scope
- make future proof-loop widening, helper-free Wasm widening, Rust round-trip activation, or Track `C` promotion require fresh decision and plan updates

## Done when

- `README.md`, `ARCHITECTURE.md`, and this file name the same active target
- Track `A` and Track `B` both emit decision-grade strongest-baseline surface evaluations and a repository-level continuation decision
- the mandatory direct-source and typed-AST baselines are executable, fair, and required on the frozen 11-case proof-loop corpus
- claim mode fails unless the active continuation outcome is `SCIR_NECESSARY`
- benchmark schemas, example artifacts, and doctrine surfaces agree on continuation outcomes, strongest-baseline attribution, contamination controls, and reproducibility requirements
- retained Track `C` sample artifacts and doctrine remain synchronized to the frozen executable proof-loop case set
- `python scripts/run_repo_validation.py` passes with Rust, Wasm, and Track `C` retained as support lanes only
- completion evidence is recorded in the active plan

## Plan

- `plans/2026-04-13-strong-baseline-falsification-phase.md`
