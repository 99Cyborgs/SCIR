---
name: scir-queue-reactivation
description: Reactivate a stalled, empty-by-design, or contradictory SCIR execution queue into one explicit next tranche with synchronized governance artifacts. Use when `EXECUTION_QUEUE.md`, queue exports, checkpoint posture, and active plans need reconciliation before governed work can continue.
---

# SCIR Queue Reactivation

Read [prompt.md](prompt.md) for the invocation frame and [checklist.md](checklist.md) for the re-entry checks.

## Purpose

Turn stalled execution state into one explicit next tranche or one explicit empty-by-design stop. This skill reconciles the queue markdown, checkpoint export, active plan state, and validation contract so future work resumes from one bounded successor rather than multiple contradictory handoff stories.

## When to use

- when the queue is empty by design and a new tranche may need to be selected
- when queue markdown, exports, checkpoint state, and active plans disagree
- when a tranche closed without a clean successor rationale
- when a handoff requires one bounded next item with exact validation and done evidence

## Allowed scope

- read `IMPLEMENTATION_PLAN.md`, `EXECUTION_QUEUE.md`, `VALIDATION.md`, `VALIDATION_STRATEGY.md`, `OPEN_QUESTIONS.md`, and the active dated plans under `plans/`
- update `EXECUTION_QUEUE.md`, the active dated plan, and a new dated plan if `plans/PLANS.md` requires one
- regenerate `reports/exports/execution_queue.export.json` and `reports/exports/checkpoint_closeout.export.json` through `scripts/build_execution_queue.py`
- update a fail-closed or closeout report using `.codex/templates/*.md` when needed for the tranche handoff

## Forbidden actions

- invent multiple ready items or a new queue taxonomy
- change roadmap phase order or semantics to force a successor
- mark broad work complete without evidence
- edit specs, schemas, validators, benchmarks, or product code as part of queue reactivation

## Required inputs

- `EXECUTION_QUEUE.md`
- `reports/exports/execution_queue.export.json`
- `reports/exports/checkpoint_closeout.export.json`
- `IMPLEMENTATION_PLAN.md`
- the active dated plan that governs the current work surface
- `OPEN_QUESTIONS.md` and `VALIDATION.md`

## Required outputs

- exactly one of:
  - one ready queue item with queue ID, scope, touched surfaces, validation, done evidence, and successor rationale
  - one explicit empty-by-design state with no-successor rationale and re-entry conditions
- synchronized queue and checkpoint exports when queue state changes
- one concise reactivation summary naming the next tranche or the fail-closed stop

## Validation sequence

1. Run `python scripts/build_execution_queue.py --mode check`.
2. If queue or checkpoint state must change, update the authoritative markdown sources first.
3. Regenerate exports with `python scripts/build_execution_queue.py --mode write`.
4. Re-run `python scripts/build_execution_queue.py --mode check`.
5. Run `python scripts/validate_repo_contracts.py --mode validate`.
6. If queue re-entry or closeout state changed, run `python scripts/run_repo_validation.py` before calling the tranche state synchronized.

## Done criteria

- the queue is either `READY` with exactly one bounded ready item or `EMPTY BY DESIGN` with an explicit no-successor rationale
- queue markdown and both exports agree
- the active dated plan status agrees with the queue state
- the selected tranche has exact validation commands and done evidence
- no contradictory ready-item story remains

## Failure conditions

- no authoritative roadmap or active plan source can justify a safe successor
- multiple plausible successor items remain and the repo does not rank them
- queue/export drift depends on schema or script changes outside queue-surface scope
- reactivation would require semantics, benchmark posture, or backend/frontend scope changes

## Escalation rules

- escalate when successor selection needs a decision-register change or a new roadmap choice
- escalate when an `OPEN_QUESTIONS.md` blocker controls tranche ordering
- escalate when a safe successor would require edits outside queue, plan, or export surfaces
