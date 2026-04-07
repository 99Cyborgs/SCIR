# 2026-04-06 Q-06-009 Lock Track C Provenance-Note Format

Status: complete
Owner: Codex
Date: 2026-04-06

## Objective

Lock the minimal markdown note shape that must accompany any future non-editorial Track `C` sample refresh so regeneration provenance stays auditable and consistently readable.

## Scope

- add an authoritative minimal provenance-note format to shared benchmark metadata
- mirror that note-format contract in the machine-checkable benchmark doctrine sections
- state the exact markdown template in the benchmark and reports readmes
- make benchmark and repo validation fail if the note-format doctrine drifts or the operator-facing template disappears
- record the governance decision and advance the queue to the next bounded Track `C` follow-on

## Non-goals

- no change to benchmark schemas or Track `C` sample JSON shape
- no new Track `C` runner behavior
- no weakening of the retained pilot's synchronization, provenance, or re-decision boundaries
- no promotion of Track `C` into the default executable benchmark gate

## Touched files

- `BENCHMARK_STRATEGY.md`
- `benchmarks/README.md`
- `benchmarks/tracks.md`
- `reports/README.md`
- `scripts/benchmark_contract_metadata.py`
- `scripts/benchmark_contract_dry_run.py`
- `scripts/validate_repo_contracts.py`
- `DECISION_REGISTER.md`
- `EXECUTION_QUEUE.md`
- `reports/exports/decision_register.export.json`
- `reports/exports/execution_queue.export.json`
- `plans/2026-04-01-mvp-narrowing-and-contract-hardening.md`

## Invariants that must remain true

- Track `A` and Track `B` remain the only default executable benchmark gates
- the Track `C` pilot remains explicit opt-in only
- `c_opaque_call` remains boundary-accounting-only
- non-editorial Track `C` sample refreshes remain bound to the opt-in runner outputs
- the provenance note stays minimal and field-limited rather than turning into a broader benchmark-report contract

## Risks

- the note format can become ambiguous if the field names or heading are left implied instead of explicit
- benchmark doctrine and operator-facing readmes can drift if they describe the same note shape differently
- queue and decision exports can fall out of sync if the markdown authorities move without regenerated exports

## Validation steps

- `python scripts/benchmark_contract_dry_run.py --include-track-c-pilot`
- `python scripts/validate_repo_contracts.py --mode validate`
- `python scripts/validate_repo_contracts.py --mode test`
- `python scripts/build_execution_queue.py --mode write`
- `python scripts/build_execution_queue.py --mode check`
- `python scripts/run_repo_validation.py --include-track-c-pilot`

## Rollback strategy

Revert the provenance-note metadata, doctrine, validator checks, and governance/export updates as one slice if the format cannot remain narrow and synchronized with the retained Track `C` pilot contract.

## Evidence required for completion

- shared metadata exports an explicit minimal Track `C` provenance-note format
- benchmark doctrine and operator readmes expose the same note format without weakening the existing provenance requirements
- benchmark and repository validation fail when the note-format doctrine drifts or the operator template disappears
- the decision register and execution queue record the new note-format boundary and next bounded follow-on

## Completion evidence

- `scripts/benchmark_contract_metadata.py` now exports the exact minimal Track `C` provenance-note heading and field bullets for non-editorial sample refreshes
- `BENCHMARK_STRATEGY.md` and `benchmarks/tracks.md` now mirror that note format in machine-checkable list form, and `benchmarks/README.md` plus `reports/README.md` now publish the exact markdown template operators must use
- `scripts/benchmark_contract_dry_run.py` and `scripts/validate_repo_contracts.py` now fail if the Track `C` provenance-note format drifts or if the benchmark and reports readmes stop publishing the template
- `DR-037` records the note-format boundary, `Q-06-009` is closed, and the execution queue now advances to `Q-06-010`
