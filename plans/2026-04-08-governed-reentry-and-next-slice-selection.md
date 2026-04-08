# 2026-04-08 Governed Re-entry And Next Slice Selection

Status: complete
Owner: Codex
Date: 2026-04-08

## Objective

Close the current validated dirty slice into one clean governance-bound baseline, then reopen the execution queue with one bounded roadmap-aligned successor item that is immediately executable without introducing new governance primitives.

## Scope

- validate the current dirty slice and normalize any stale queue, checkpoint, plan, or export references needed for a clean baseline
- create the baseline closeout commit for the current dirty slice
- evaluate bounded non-hardening successor options against the active roadmap and implementation phases
- define exactly one successor queue item with explicit scope, validation, evidence binding, reversibility, and risks
- update queue and export artifacts so re-entry is explicit, synchronized, and reproducible

## Non-goals

- invent multiple successor items or a new queue taxonomy
- widen SCIR-H, SCIR-L, importer, backend, or benchmark semantics beyond current doctrine
- weaken empty-queue fail-closed behavior or checkpoint evidence binding
- introduce new governance primitives, dependencies, or build steps

## Touched files

- `plans/2026-04-08-governed-reentry-and-next-slice-selection.md`
- `EXECUTION_QUEUE.md`
- `reports/exports/execution_queue.export.json`
- `reports/exports/checkpoint_closeout.export.json`
- `plans/2026-04-01-mvp-narrowing-and-contract-hardening.md`
- `DECISION_REGISTER.md` if successor re-entry changes decision posture

## Invariants that must remain true

- `SCIR-H` remains the only normative semantic representation
- `SCIR-L` remains derivative-only and may not gain new semantics
- queue re-entry remains fail-closed until the successor item, validation impact, and exports agree
- exactly one bounded successor item is created
- the successor item advances roadmap phase work rather than another hygiene-only slice

## Risks

- the current checkpoint export may be synchronized to the dirty workspace but not to the intended clean post-commit baseline
- successor selection could drift into vague hardening work unless file scope, exclusions, and measurable outcomes are made explicit
- queue, checkpoint, and plan artifacts can diverge if regenerated against different git or working-tree states

## Validation steps

- `python scripts/build_execution_queue.py --mode check`
- `python scripts/validate_repo_contracts.py --mode validate`
- `python scripts/validate_repo_contracts.py --mode test`
- `python scripts/run_repo_validation.py`

## Rollback strategy

Revert the re-entry patch set as one unit if the baseline closeout, successor definition, and regenerated exports cannot be kept synchronized under the existing queue and repository validation gates.

## Evidence required for completion

- one atomic baseline commit closes the current dirty slice
- one bounded successor item is present in `EXECUTION_QUEUE.md`
- queue and checkpoint exports are schema-valid and synchronized
- validation results are recorded against the final re-opened queue state

## Successor selection

- Selected next item: `Q-03-002 - Lock Rust ownership-mode mapping across importer evidence and optional H -> L validation`
- Justification: Phase 3 Rust importer alignment is the smallest roadmap advance that is not just more hardening. The active Rust subset already carries the ownership-bearing and unsafe-boundary cases, the optional Rust validation lane already exists, and the current validation stack can enforce this alignment without new governance machinery.
- Why not alternatives: Python proof-loop work would reduce to more hardening of an already active path; broader Wasm work would reopen higher-risk backend scope and contract expansion; Track `A` / `B` reproducibility work is benchmark hardening rather than a new roadmap slice.
- Phase alignment: `Rust safe-subset importer`
- Expected measurable outcome: Rust importer scope, metadata, fixture bundles, and the optional Rust `H -> L` validation lane agree on the admitted ownership-bearing cases and fail closed on future drift.

## Completion evidence

- Baseline closeout commit `c653eb5` now closes the validated dirty slice as one governance-bound checkpoint commit with synchronized queue and checkpoint exports.
- `EXECUTION_QUEUE.md` now reopens the queue with exactly one ready successor item, `Q-03-002`, and removes the empty-by-design no-successor posture while preserving `Q-06-012` as the last completed item.
- `plans/2026-04-01-mvp-narrowing-and-contract-hardening.md` now returns to `in-progress` so the active queue source matches the reopened queue state without inventing a new governance primitive.
- Queue and checkpoint exports were regenerated from the updated markdown state and then re-written once more so the dirty-state checkpoint captured both export files in the active re-entry slice.
- Passed `python scripts/build_execution_queue.py --mode check`
- Passed `python scripts/validate_repo_contracts.py --mode validate`
- Passed `python scripts/validate_repo_contracts.py --mode test`

## CLOSEOUT

- Scope completed: the dirty governance slice is closed into a validator-clean baseline and the queue is re-opened with one bounded Phase 3 Rust importer alignment item that is immediately executable.
- Invariants satisfied: `SCIR-H` remained the only semantic authority, `SCIR-L` remained derivative-only, queue re-entry stayed fail-closed until the successor item was explicit, and no new unsupported surface was activated.
- Residual risks: the selected Rust alignment slice still has to avoid implying Rust round-trip, backend, or benchmark support; broader Wasm or benchmark work remains intentionally deferred until a later deliberate re-entry.
- Validation status: passed on 2026-04-08 via `python scripts/build_execution_queue.py --mode check`, `python scripts/validate_repo_contracts.py --mode validate`, and `python scripts/validate_repo_contracts.py --mode test`.
