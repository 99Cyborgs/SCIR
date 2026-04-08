---
name: scir-repo-contract-audit
description: Restate and enforce the current SCIR MVP repo contract before any tranche begins. Use when starting governed SCIR work, reopening context after a pause, checking whether a request would widen scope, or preparing a plan for work that touches governed surfaces, queue state, or validation posture.
---

# SCIR Repo Contract Audit

Read [prompt.md](prompt.md) for a Codex-ready invocation frame and [checklist.md](checklist.md) for the stepwise audit checks.

## Purpose

Restate the active SCIR repo constitution before implementation begins. This skill converts the root governance set, current queue state, and validation contract into one explicit go or no-go tranche boundary so work starts from admitted MVP surfaces instead of repo improvisation.

## When to use

- before starting any nontrivial SCIR tranche
- after a pause, handoff, or context reset
- when a request might widen frontend, backend, benchmark, or automation scope
- before creating or updating a plan for work that crosses governed surfaces

## Allowed scope

- read root governance files named in `AGENTS.md`
- read `EXECUTION_QUEUE.md`, `reports/exports/execution_queue.export.json`, and `reports/exports/checkpoint_closeout.export.json`
- read `plans/PLANS.md` and the active dated plan relevant to the tranche
- update only the active task plan under `plans/` or a task-scoped report derived from `.codex/templates/*.md` when the current tranche explicitly requires it

## Forbidden actions

- rewrite root architecture, roadmap, benchmark, or validator doctrine as part of the audit
- treat reports, exports, `SCIR-Hc`, or `SCIR-L` artifacts as semantic authority
- reactivate deferred TypeScript, Track `D`, native, `D-JS`, or broad tooling paths
- begin code, schema, or benchmark changes before the audit resolves authority conflicts

## Required inputs

- repo root and tranche objective
- `AGENTS.md`, `SYSTEM_BOUNDARY.md`, `REPO_MAP.md`, `ARCHITECTURE.md`, `IMPLEMENTATION_PLAN.md`, `VALIDATION.md`, `VALIDATION_STRATEGY.md`, and `BENCHMARK_STRATEGY.md`
- `EXECUTION_QUEUE.md` plus the queue and checkpoint exports
- `plans/PLANS.md` when the tranche meets a mandatory-plan condition

## Required outputs

- one compact contract summary with `Confirmed scope`, `Deferred scope`, `Hard invariants`, `Allowed tranche surfaces`, `Forbidden widening moves`, and `Canonical validation path`
- one explicit `Go / no-go` decision for the proposed tranche
- one next action: start the tranche, update a plan, hand off to another SCIR skill, or stop with a fail-closed report

## Validation sequence

1. Read the root `AGENTS.md` read order and current queue/checkpoint state before editing anything.
2. Run `python scripts/build_execution_queue.py --mode check`.
3. Run `python scripts/validate_repo_contracts.py --mode validate`.
4. If the audit writes a plan or task report, rerun `python scripts/validate_repo_contracts.py --mode validate`.
5. Name the downstream tranche validation gate from `VALIDATION.md` or `VALIDATION_STRATEGY.md`; use `python scripts/run_repo_validation.py` unless the tranche is explicitly narrower and a smaller validated gate is sufficient.

## Done criteria

- the required outputs are present
- active scope and deferred scope are explicit
- any mandatory-plan requirement is satisfied
- no authority conflict is hidden behind inference
- the tranche ends with one bounded next action or an explicit fail-closed stop

## Failure conditions

- required authority files are missing or materially conflict
- queue/checkpoint validation fails
- the requested work depends on a deferred or unsupported surface
- the tranche would require a generic autonomous maintainer pattern

## Escalation rules

- escalate when a request needs roadmap, phase-order, or architecture changes
- escalate when queue re-entry would need a new successor item but no authoritative source selects one
- escalate when an unresolved `OPEN_QUESTIONS.md` blocker or decision-register gap controls the tranche boundary
