# Preflight Checks

- [ ] Read `AGENTS.md` and the root read-order files it requires.
- [ ] Read `EXECUTION_QUEUE.md` and the queue/checkpoint exports.
- [ ] Check whether `plans/PLANS.md` makes a dated plan mandatory.
- [ ] State the tranche objective in one sentence.

# In-Flight Checks

- [ ] Separate confirmed facts from inference.
- [ ] List admitted surfaces and deferred surfaces explicitly.
- [ ] Name the hard invariants that block scope widening.
- [ ] Reduce the tranche to one bounded touched-surface set.

# Output Checks

- [ ] Produce `Confirmed scope`.
- [ ] Produce `Deferred scope`.
- [ ] Produce `Hard invariants`.
- [ ] Produce `Allowed tranche surfaces`.
- [ ] Produce `Forbidden widening moves`.
- [ ] Produce `Canonical validation path`.
- [ ] Produce one `Go / no-go` decision and one `Next action`.

# Validation Checks

- [ ] Run `python scripts/build_execution_queue.py --mode check`.
- [ ] Run `python scripts/validate_repo_contracts.py --mode validate`.
- [ ] If a plan or task report was written, rerun `python scripts/validate_repo_contracts.py --mode validate`.
- [ ] Name the downstream tranche validation gate without claiming it passed unless it was actually run.

# Closeout Checks

- [ ] No authority conflict is hidden.
- [ ] No deferred surface was silently admitted.
- [ ] No code, schema, benchmark, or doctrine edit started under an unresolved contract.
- [ ] The tranche either has one bounded next action or an explicit fail-closed stop.
