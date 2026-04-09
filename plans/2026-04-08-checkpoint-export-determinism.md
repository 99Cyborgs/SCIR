# 2026-04-08 Checkpoint Export Determinism

Status: complete
Owner: Codex
Date: 2026-04-08

## Objective

Make `python scripts/build_execution_queue.py --mode write` produce a `checkpoint_closeout` export that immediately passes `--mode check` in the same clean baseline, instead of drifting because the generator observes its own managed export writes as working-tree dirtiness.

## Scope

- stabilize checkpoint git-context capture around the queue-export and checkpoint-export files managed by `build_execution_queue.py`
- add regression coverage proving write-then-check determinism in a temporary git repo
- regenerate the checked-in execution-queue and checkpoint-closeout exports after the fix

## Non-goals

- select a new roadmap successor or reopen the queue with a substantive ready item
- change queue doctrine, checkpoint schema shape, or decision-register semantics
- widen SCIR-H, SCIR-L, importer, backend, or benchmark scope

## Touched files

- `plans/2026-04-08-checkpoint-export-determinism.md`
- `scripts/build_execution_queue.py`
- `tests/test_build_execution_queue.py`
- `reports/exports/execution_queue.export.json`
- `reports/exports/checkpoint_closeout.export.json`

## Invariants that must remain true

- the execution queue remains `EMPTY BY DESIGN` unless a separately-authorized roadmap successor is selected
- checkpoint exports still record unrelated working-tree dirtiness and commit context explicitly
- `SCIR-H` remains the only normative semantic representation
- `SCIR-L` remains derivative-only

## Risks

- over-filtering git status could hide real working-tree dirtiness instead of only the managed export files
- the regression test could pass only because of temp-repo setup differences instead of the real write/check path
- regenerating exports after the fix could expose another checkpoint-closeout assumption beyond self-drift

## Validation steps

- `python -m unittest tests.test_build_execution_queue`
- `python scripts/build_execution_queue.py --mode check`
- `python scripts/validate_repo_contracts.py --mode validate`
- `python scripts/run_repo_validation.py`

## Rollback strategy

Revert the deterministic-export patch set as one slice if managed-export filtering cannot be kept narrow enough to preserve real dirty-tree evidence or if queue/checkpoint synchronization still fails after regeneration.

## Evidence required for completion

- write-then-check determinism is covered by an automated test
- `build_execution_queue.py` still records unrelated dirty files while ignoring only its own managed export writes
- the checked-in execution-queue and checkpoint-closeout exports pass repo validation again

## Completion evidence

- `scripts/build_execution_queue.py` now filters only `reports/exports/execution_queue.export.json` and `reports/exports/checkpoint_closeout.export.json` out of checkpoint working-tree status, so `--mode write` no longer makes the checkpoint export immediately fail `--mode check`.
- `tests/test_build_execution_queue.py` now proves both write-then-check determinism and preservation of unrelated dirty-file reporting in a temporary git repo.
- `EXECUTION_QUEUE.md` and the regenerated queue/checkpoint exports now record this bounded hardening slice as the last completed item while keeping the queue `EMPTY BY DESIGN`.
- Passed `python -m unittest tests.test_build_execution_queue`
- Passed `python scripts/build_execution_queue.py --mode check`
- Passed `python scripts/validate_repo_contracts.py --mode validate`
- Passed `python scripts/run_repo_validation.py`

## CLOSEOUT

- Scope completed: checkpoint-closeout export generation is now stable against its own managed export writes without weakening unrelated dirty-tree evidence.
- Invariants satisfied: the queue stayed `EMPTY BY DESIGN`, checkpoint artifacts still record real working-tree dirtiness explicitly, and no SCIR semantic or benchmark scope widened.
- Residual risks: any future managed export added to `build_execution_queue.py` will need to be added to the narrow ignore set and kept covered by the determinism test.
