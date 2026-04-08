# 2026-04-08 SCIR Tranche Skill Pack

Status: complete
Owner: Codex
Date: 2026-04-08

## Objective

Add a bounded repo-local Codex skill pack that helps future SCIR tranche work start from the current repo contract, reactivate the queue without drift, and harden provenance continuity without widening product scope.

## Scope

- add three new repo-local skills under `.codex/skills/`
- add one thin `.codex` index for the tranche-operator pack
- add minimal repo-local tranche, failure, and closeout templates under `.codex/templates/`
- align the new skills to the existing SCIR skill naming and discovery convention
- validate the skill folders and the repository after the additions land

## Non-goals

- change SCIR semantics, schemas, validator doctrine, benchmark doctrine, or roadmap sequencing
- add a generic repo-maintainer or broad autonomous-write skill
- rewrite queue, checkpoint, or decision artifacts unless validation requires a narrow fix
- add production dependencies, services, or build steps

## Touched files

- `plans/2026-04-08-scir-tranche-skill-pack.md`
- `.codex/README.md`
- `.codex/templates/tranche_pr.md`
- `.codex/templates/failure_report.md`
- `.codex/templates/closeout_report.md`
- `.codex/skills/scir-repo-contract-audit/`
- `.codex/skills/scir-queue-reactivation/`
- `.codex/skills/scir-provenance-continuity/`
- `reports/exports/checkpoint_closeout.export.json`

## Invariants that must remain true

- `SCIR-H` remains the only normative semantic authority.
- `SCIR-L` remains derivative-only and provenance-bound.
- queue re-entry remains fail-closed and export-synchronized.
- the new skills stay limited to the admitted SCIR MVP and current governance surfaces.
- the pack does not introduce a general-purpose autopilot or vague future-agent framework.

## Risks

- the new skills could duplicate existing SCIR auditors instead of serving as tranche-entry operators
- generic wording could let the pack trigger outside the admitted SCIR MVP boundary
- prompt or checklist resources could drift from current queue, validation, or provenance contracts if they are not grounded to exact repo paths and commands

## Validation steps

- `python C:/Users/Forre/.codex/skills/.system/skill-creator/scripts/quick_validate.py G:/GitHub/incubate/SCIR/.codex/skills/scir-repo-contract-audit`
- `python C:/Users/Forre/.codex/skills/.system/skill-creator/scripts/quick_validate.py G:/GitHub/incubate/SCIR/.codex/skills/scir-queue-reactivation`
- `python C:/Users/Forre/.codex/skills/.system/skill-creator/scripts/quick_validate.py G:/GitHub/incubate/SCIR/.codex/skills/scir-provenance-continuity`
- `python scripts/run_repo_validation.py`

## Rollback strategy

Remove the three new skill directories, the `.codex` index and templates added for this tranche, and this dated plan file if the pack proves invalid, redundant, or inconsistent with the repo validation gate.

## Evidence required for completion

- each new skill has a valid `SKILL.md`
- each new skill includes a grounded `prompt.md` and `checklist.md`
- the `.codex` index explains the bounded tranche-operator entry order
- the templates are minimal, executable, and tied to existing governance surfaces
- the listed validation commands pass against the final working tree

## Completion evidence

- Added `.codex/README.md` plus `.codex/templates/tranche_pr.md`, `.codex/templates/failure_report.md`, and `.codex/templates/closeout_report.md` as minimal repo-local operator aids.
- Added `.codex/skills/scir-repo-contract-audit/`, `.codex/skills/scir-queue-reactivation/`, and `.codex/skills/scir-provenance-continuity/` with `SKILL.md`, `prompt.md`, `checklist.md`, and discovery metadata aligned to the existing `scir-` repo convention.
- Kept all three skills fail-closed on deferred surfaces, queue drift, provenance theater, and generic autonomous-maintainer behavior.
- Ran `python C:/Users/Forre/.codex/skills/.system/skill-creator/scripts/quick_validate.py` for each new skill and all three passed.
- Ran `python scripts/run_repo_validation.py`; it passed after regenerating the checkpoint export through `python scripts/build_execution_queue.py --mode write` and confirming synchronization with `python scripts/build_execution_queue.py --mode check`.

## CLOSEOUT

- Scope completed: the repo now has a bounded tranche-operator skill pack for contract audit, queue reactivation, and provenance continuity, plus minimal supporting templates and index documentation.
- Invariants satisfied: `SCIR-H` stayed authoritative, `SCIR-L` stayed derivative-only, queue re-entry remained fail-closed, and no new frontend, backend, benchmark, or platform path was activated.
- Residual risks: the new skills cite current queue, validation, and provenance surfaces, so later governance edits must keep those references current; the pack deliberately stops short of any broad autonomous maintenance surface.
- Validation status: passed on 2026-04-08 via three `quick_validate.py` runs, `python scripts/build_execution_queue.py --mode check`, and `python scripts/run_repo_validation.py`.
