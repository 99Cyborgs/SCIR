# Invocation Prompt

```text
Use $scir-repo-contract-audit at G:/GitHub/incubate/SCIR/.codex/skills/scir-repo-contract-audit before starting this tranche. Restate the current SCIR MVP contract from the repo’s governing files, name the exact surfaces this tranche is allowed to touch, identify deferred or forbidden surfaces, select the smallest sufficient validation gate, and fail closed if the request would widen scope or if queue and authority surfaces disagree.
```

# Task Model

Translate one requested tranche into an explicit SCIR repo contract before implementation starts. The output is a go or no-go tranche boundary, not a speculative design pass.

# Confirmed Facts

- Root authority starts with `AGENTS.md`, then the root read-order files named there.
- `SCIR-H` is the only normative semantic authority.
- `SCIR-L` is derivative-only.
- The current canonical Windows-safe repo validation entrypoint is `python scripts/run_repo_validation.py`.
- Queue state and checkpoint posture are governed by `EXECUTION_QUEUE.md`, `reports/exports/execution_queue.export.json`, `reports/exports/checkpoint_closeout.export.json`, and `scripts/build_execution_queue.py`.

# Explicit Constraints

- Do not widen frontend, backend, benchmark, or tooling scope.
- Do not treat exports, reports, `SCIR-Hc`, or `SCIR-L` as semantic authority.
- Do not begin implementation while authority conflicts, queue drift, or mandatory-plan gaps remain unresolved.
- Keep the audit read-mostly; write only the active plan or a scoped report if the tranche requires it.

# Execution Steps

1. Read the root governance files in the `AGENTS.md` order.
2. Read the current queue and checkpoint surfaces.
3. Check whether `plans/PLANS.md` makes a dated plan mandatory for the requested tranche.
4. Reduce the request to allowed touched surfaces, deferred surfaces, hard invariants, and the exact validation gate.
5. If the tranche is admissible, return one bounded next action and the next relevant SCIR skill. If not, stop and emit a fail-closed result.

# Required Outputs

- `Confirmed scope`
- `Deferred scope`
- `Hard invariants`
- `Allowed tranche surfaces`
- `Forbidden widening moves`
- `Canonical validation path`
- `Go / no-go decision`
- `Next action`

# Validation

- `python scripts/build_execution_queue.py --mode check`
- `python scripts/validate_repo_contracts.py --mode validate`
- downstream validation gate named from `VALIDATION.md` or `VALIDATION_STRATEGY.md`

# Fail-Closed Rules

- Stop if the tranche depends on deferred TypeScript, Track `D`, native, `D-JS`, or broad platform work.
- Stop if root authority files disagree and the disagreement changes scope, sequencing, or semantics.
- Stop if queue/export validation fails and the tranche depends on queue state.
- Stop if the request requires broad autonomous write authority instead of one bounded tranche.
