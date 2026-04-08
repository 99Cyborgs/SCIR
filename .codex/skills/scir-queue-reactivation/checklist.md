# Preflight Checks

- [ ] Read `EXECUTION_QUEUE.md`.
- [ ] Read `reports/exports/execution_queue.export.json`.
- [ ] Read `reports/exports/checkpoint_closeout.export.json`.
- [ ] Read `IMPLEMENTATION_PLAN.md` and the active dated plan.
- [ ] Read `OPEN_QUESTIONS.md` if blockers or sequencing uncertainty appear.

# In-Flight Checks

- [ ] Determine whether the queue should be `READY` or `EMPTY BY DESIGN`.
- [ ] Keep at most one ready item.
- [ ] Keep successor scope bounded to one tranche.
- [ ] Keep touched surfaces, validation, and done evidence explicit.
- [ ] Keep queue, checkpoint, and active-plan narratives aligned.

# Output Checks

- [ ] Produce one bounded successor item or one no-successor rationale.
- [ ] Name exact touched governance artifacts.
- [ ] Name exact validation commands.
- [ ] Name exact done evidence.
- [ ] Name exact escalation conditions.

# Validation Checks

- [ ] Run `python scripts/build_execution_queue.py --mode check`.
- [ ] If queue state changed, run `python scripts/build_execution_queue.py --mode write`.
- [ ] Re-run `python scripts/build_execution_queue.py --mode check`.
- [ ] Run `python scripts/validate_repo_contracts.py --mode validate`.
- [ ] If queue state changed, run `python scripts/run_repo_validation.py`.

# Closeout Checks

- [ ] No contradictory ready items remain.
- [ ] Queue markdown and exports are synchronized.
- [ ] The active plan status matches the queue state.
- [ ] Empty-by-design posture stays explicit if no safe successor exists.
- [ ] No semantic, benchmark, or product-scope changes were smuggled into queue work.
