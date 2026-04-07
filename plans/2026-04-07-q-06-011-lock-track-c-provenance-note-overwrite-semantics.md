# 2026-04-07 Q-06-011 Lock Track C Provenance-Note Overwrite Semantics

Status: complete
Owner: Codex
Date: 2026-04-07

## Objective

Lock deterministic overwrite semantics for the fixed checked-in Track `C` provenance note so future non-editorial sample refreshes replace one canonical note artifact instead of accumulating ambiguous residue at the same path.

## Scope

- add one authoritative Track `C` provenance-note overwrite rule to shared benchmark metadata
- mirror that overwrite rule in benchmark doctrine and operator readmes
- make benchmark and repository validation fail if the overwrite rule drifts from the shared contract
- record the governance boundary in the decision register

## Non-goals

- no new Track `C` runner behavior
- no new benchmark artifact type or schema
- no widening of the default benchmark gate
- no relaxation of the retained pilot's synchronization, provenance, location, or re-decision boundaries
- no queue expansion beyond the current bounded governance slice

## Touched files

- `plans/2026-04-07-q-06-011-lock-track-c-provenance-note-overwrite-semantics.md`
- `BENCHMARK_STRATEGY.md`
- `benchmarks/tracks.md`
- `benchmarks/README.md`
- `reports/README.md`
- `scir/contract_docs.py`
- `scripts/benchmark_contract_metadata.py`
- `scripts/benchmark_contract_dry_run.py`
- `scripts/validate_repo_contracts.py`
- `DECISION_REGISTER.md`
- `reports/exports/decision_register.export.json`

## Invariants that must remain true

- Track `A` and Track `B` remain the only default executable benchmark gates
- Track `C` remains explicit opt-in only
- the fixed provenance note path remains `reports/examples/benchmark_track_c_refresh_provenance.example.md`
- the checked-in note remains generator-backed from the same Track `C` sample manifest and result contract
- non-editorial refreshes remain provenance-bound and governance-gated when posture changes

## Risks

- overwrite wording can drift between metadata, doctrine, and validator checks if one surface is edited manually
- overly broad overwrite wording could accidentally legitimize deleting neighboring sample artifacts rather than replacing only the fixed note
- updating decision-register doctrine without matching validation checks would weaken the point of the new boundary

## Validation steps

- `python scripts/validate_repo_contracts.py --mode validate`
- `python scripts/validate_repo_contracts.py --mode test`
- `python scripts/benchmark_contract_dry_run.py --include-track-c-pilot`

## Rollback strategy

Revert the overwrite-rule metadata, doctrine wording, validator checks, and decision-register entry together if the fixed-note replacement rule proves unclear or destabilizes existing benchmark validation.

## Evidence required for completion

- shared metadata exports one explicit overwrite rule for the fixed Track `C` provenance note
- benchmark doctrine and operator readmes state that non-editorial refreshes replace the entire checked-in note at the fixed path
- benchmark and repository validation fail if the overwrite rule drifts from shared metadata
- the decision register records the overwrite-semantics boundary

## Completion evidence

- `scripts/benchmark_contract_metadata.py` now exports `non_editorial_sample_refresh_note_overwrite` for Track `C`, and rendered contract docs consume that field through `scir/contract_docs.py`
- `BENCHMARK_STRATEGY.md`, `benchmarks/tracks.md`, `benchmarks/README.md`, and `reports/README.md` now state that non-editorial refreshes replace the fixed checked-in provenance note rather than appending history or creating sibling variants
- `scripts/benchmark_contract_dry_run.py` and `scripts/validate_repo_contracts.py` now fail on drift in the overwrite-semantics section and on missing operator-facing overwrite wording
- `DR-039` records the overwrite-in-place boundary for the retained Track `C` provenance note
- passed `python scripts/validate_repo_contracts.py --mode validate`
- passed `python scripts/validate_repo_contracts.py --mode test`
- passed `python scripts/benchmark_contract_dry_run.py --include-track-c-pilot`

## CLOSEOUT

- Scope completed: overwrite-in-place semantics are now explicit across metadata, doctrine, validator checks, and the decision register for the single retained Track `C` provenance note.
- Invariants satisfied: the retained note path, note format, runner-derived provenance fields, and non-default Track `C` posture remained unchanged while only the replacement rule tightened.
- Residual risks: future queue work is not implied by this slice; any further governance around Track `C` now requires explicit roadmap selection rather than automatic queue continuation.
- Validation status: passed on 2026-04-07 via `python scripts/build_execution_queue.py --mode check`, `python scripts/validate_repo_contracts.py --mode validate`, `python scripts/validate_repo_contracts.py --mode test`, `python scripts/benchmark_contract_dry_run.py --include-track-c-pilot`, and `python scripts/run_repo_validation.py --include-track-c-pilot`.
