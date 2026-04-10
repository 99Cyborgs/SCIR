# Repository reset consolidation

Status: complete
Owner: Codex
Date: 2026-04-10

## Objective

Reset `main` to a smaller, implementation-led baseline centered on the Python subset importer, canonical `SCIR-H`, and validator hardening.

## Scope

- remove tracked generated artifacts and repeated sweep/benchmark outputs
- replace queue-era operating surfaces with `CURRENT_FOCUS.md` and `BACKLOG.md`
- simplify repository validation to the consolidated layout
- update root docs so the active MVP lane is explicit
- salvage only minimal non-generated value from `codex/validation-hardening-worktree`

## Non-goals

- grammar widening
- backend widening
- release-bundle activation
- broad benchmark redesign
- merging any Codex branch wholesale

## Touched files

- AGENTS.md
- README.md
- SYSTEM_BOUNDARY.md
- REPO_MAP.md
- ARCHITECTURE.md
- DECISION_REGISTER.md
- VALIDATION_STRATEGY.md
- reports/README.md
- reports/repo_reset_report.md
- reports/repo_reset_followthrough.md
- scripts/validate_repo_contracts.py
- scripts/run_repo_build.py
- scripts/run_repo_lint.py
- scripts/run_repo_validation.py
- scripts/scir_sweep.py
- scripts/benchmark_contract_dry_run.py
- .gitignore
- CURRENT_FOCUS.md
- BACKLOG.md
- pyproject.toml
- Makefile
- ci/validation_pipeline.md
- AGENTS.md

## Invariants that must remain true

- `SCIR-H` remains the only normative semantic authority
- `SCIR-L` remains derivative-only
- future grammar widening remains spec-first
- release-bundle machinery remains opt-in only
- default validation stays runnable from `python scripts/run_repo_validation.py`

## Risks

- over-pruning docs or tracked examples that the current validation stack still consumes
- leaving stale references to removed queue/export machinery in root docs or scripts
- removing tracked artifacts without ignoring future outputs, causing immediate repo re-pollution

## Validation steps

- `python scripts/validate_repo_contracts.py --mode validate`
- `python scripts/validate_repo_contracts.py --mode audit`
- `python scripts/run_repo_lint.py`
- `python scripts/run_repo_build.py`
- `python scripts/run_repo_validation.py`

## Rollback strategy

Reapply only the removed files or checks that prove to be validator-consumed, keeping the consolidated operating model intact.

## Evidence required for completion

- `reports/repo_reset_report.md`
- `reports/repo_reset_followthrough.md`
- successful `python scripts/run_repo_validation.py`
- diff review showing tracked artifact and queue-surface removal
- branch cleanup showing `main` as the only remaining operating branch
