# Invocation Prompt

```text
Use $scir-queue-reactivation at G:/GitHub/incubate/SCIR/.codex/skills/scir-queue-reactivation to reconcile the current SCIR execution queue, checkpoint export, and active plan state. Select exactly one bounded next tranche or keep the queue explicitly empty by design, synchronize the governance artifacts, list exact validation commands and done evidence, and fail closed if no authoritative successor can be justified.
```

# Task Model

Convert the current queue and checkpoint posture into one explicit next tranche or one explicit empty-by-design stop. The task is governance synchronization, not product expansion.

# Confirmed Facts

- Queue truth is shared between `EXECUTION_QUEUE.md`, `reports/exports/execution_queue.export.json`, `reports/exports/checkpoint_closeout.export.json`, and `scripts/build_execution_queue.py`.
- `scripts/build_execution_queue.py` validates both `READY` and `EMPTY_BY_DESIGN` states and enforces queue re-entry markers.
- Queue re-entry requires roadmap selection, one bounded next item, validator/export impact assessment, and synchronized exports.
- `python scripts/run_repo_validation.py` already includes queue and checkpoint checks in the blocking repo gate.

# Explicit Constraints

- Create at most one ready item.
- Do not invent a new queue format, taxonomy, or handoff primitive.
- Do not force a successor by widening specs, backend scope, benchmark scope, or roadmap sequencing.
- If no authoritative successor exists, keep the queue empty by design and say why.

# Execution Steps

1. Read the current queue markdown, queue export, checkpoint export, active dated plan, and `IMPLEMENTATION_PLAN.md`.
2. Determine whether the repo is already synchronized, needs one bounded successor item, or must remain empty by design.
3. If re-entry is warranted, define one successor with queue ID, scope, touched surfaces, validation, done evidence, and escalation conditions.
4. Update authoritative markdown sources first, then regenerate exports.
5. Revalidate and summarize the resulting tranche state.

# Required Outputs

- `Current state`
- `Selected next tranche` or `Empty-by-design rationale`
- `Touched governance artifacts`
- `Validation`
- `Done evidence`
- `Escalations`

# Validation

- `python scripts/build_execution_queue.py --mode check`
- `python scripts/build_execution_queue.py --mode write` when queue state changes
- `python scripts/validate_repo_contracts.py --mode validate`
- `python scripts/run_repo_validation.py` when the queue or checkpoint state changed

# Fail-Closed Rules

- Stop if there is no authoritative roadmap or active-plan basis for one safe successor.
- Stop if multiple successors remain equally plausible after reading the governing sources.
- Stop if synchronization would require schema, script, or doctrine edits outside queue-surface scope.
- Stop if the only way to resume work is to widen scope or weaken empty-by-design behavior.
