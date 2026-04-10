# CURRENT_FOCUS
Status: Active

## Active target

Python subset importer -> canonical `SCIR-H` -> validator hardening.

## Boundaries

- Keep `SCIR-H` as the only normative semantic authority.
- Keep `SCIR-L` derivative-only and unchanged unless validator hardening requires a spec-first correction.
- Do not widen grammar, backend scope, or benchmark scope during this item.
- Keep release-bundle machinery opt-in only.

## This item

- tighten the live repo surface around the Python-first MVP path
- keep repository validation aligned to the consolidated layout
- remove tracked generated run artifacts and queue-era control surfaces
- preserve bounded Rust importer, lowering, Wasm, and benchmark surfaces as maintained but frozen support paths

## Done when

- `README.md`, `ARCHITECTURE.md`, and this file name the same active target
- queue-era control files are no longer part of the default operating surface
- tracked generated run outputs are removed and ignored
- `python scripts/run_repo_validation.py` passes on the consolidated layout
- `reports/repo_reset_report.md` records keep/remove/archive/salvage decisions

## Plan

- `plans/2026-04-10-repo-reset-consolidation.md`
