# CURRENT_FOCUS
Status: Retired

## Repository status

Frozen and retired.

The final repository phase was the frozen 11-case Python proof-loop strong-baseline falsification for Track `A` and Track `B`.
The final repository-level outcome was `SCIR_USEFUL_BUT_UNNECESSARY`.

## Final bounded MVP kept on disk

- canonical `SCIR-H`
- derived `SCIR-Hc`
- derivative `SCIR-L`
- validator coverage for `SCIR-H`, `SCIR-Hc`, `SCIR-L`, and `SCIR-H -> SCIR-L` preservation
- Python subset import on the frozen 11-case proof loop
- Python reconstruction from validated `SCIR-H`
- bounded Rust importer-first evidence
- bounded helper-free Wasm validation for the admitted subset
- Track `A` and Track `B` benchmark harnesses

## Boundaries that still apply

- Keep `SCIR-H` as the only normative semantic authority.
- Keep `SCIR-L` derivative-only in the historical record.
- Treat the 11-case Python executable proof loop as the final admitted benchmark corpus.
- Do not widen grammar, Python scope, or backend scope in this retired repository.
- Keep Rust importer-first, helper-free Wasm bounded, and Track `C` non-default as preserved support lanes only.
- Require a new plan plus a new decision-register update before any future reactivation.
- Keep release-bundle machinery opt-in only.

## Retirement record

This file is the retirement record for the repository.

- The repository reached a decision-grade falsification phase with mandatory direct-source and typed-AST baselines.
- The final admitted result was useful but unnecessary, not continuation-justifying.
- The repository is frozen as a record of the mechanisms that were worth preserving and the thesis that was not.

## No active work

- No widening work is active.
- No new benchmark tracks are being promoted.
- No new semantic authority layers are being added.
- Successor work, if any, should be mechanism-extractive rather than SCIR-preservative.

## Plan

- `plans/2026-04-13-project-freeze-retirement-summary.md`
