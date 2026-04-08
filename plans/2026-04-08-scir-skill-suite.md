# SCIR Skill Suite

Status: complete
Owner: Codex
Date: 2026-04-08

## Objective

Add five repo-local Codex skills that encode recurring SCIR governance and implementation workflows not already covered by `scir-proof-loop-guard`.

## Scope

- create five new skill directories under `.codex/skills/`
- add SCIR-specific `SKILL.md` instructions for each skill
- add `agents/openai.yaml` metadata for each skill
- validate the new skill folders with the skill validator

## Non-goals

- change SCIR semantics, schemas, validators, or benchmark doctrine
- add new production dependencies or repo build steps
- modify the existing `scir-proof-loop-guard` skill unless validation requires it

## Touched files

- `plans/2026-04-08-scir-skill-suite.md`
- `.codex/skills/scir-spec-sync/`
- `.codex/skills/scir-tier-profile-auditor/`
- `.codex/skills/scir-lowering-provenance-check/`
- `.codex/skills/scir-importer-boundary-auditor/`
- `.codex/skills/scir-benchmark-claim-auditor/`

## Invariants that must remain true

- `SCIR-H` remains the only semantic authority.
- Skill descriptions trigger on SCIR-specific work rather than generic coding tasks.
- New skills do not widen repo claims, validation gates, or benchmark posture.
- Skill naming and metadata remain valid under the Codex skill contract.

## Risks

- overlap between new skills and `scir-proof-loop-guard` could make invocation ambiguous
- overly generic descriptions could trigger outside the intended SCIR workflows
- weak instructions could restate repo docs without adding reusable workflow value

## Validation steps

- `python C:/Users/Forre/.codex/skills/.system/skill-creator/scripts/quick_validate.py G:/GitHub/incubate/SCIR/.codex/skills/scir-spec-sync`
- `python C:/Users/Forre/.codex/skills/.system/skill-creator/scripts/quick_validate.py G:/GitHub/incubate/SCIR/.codex/skills/scir-tier-profile-auditor`
- `python C:/Users/Forre/.codex/skills/.system/skill-creator/scripts/quick_validate.py G:/GitHub/incubate/SCIR/.codex/skills/scir-lowering-provenance-check`
- `python C:/Users/Forre/.codex/skills/.system/skill-creator/scripts/quick_validate.py G:/GitHub/incubate/SCIR/.codex/skills/scir-importer-boundary-auditor`
- `python C:/Users/Forre/.codex/skills/.system/skill-creator/scripts/quick_validate.py G:/GitHub/incubate/SCIR/.codex/skills/scir-benchmark-claim-auditor`
- `python scripts/run_repo_validation.py`

## Rollback strategy

Remove the five new skill directories and this dated plan file if the skills prove invalid or redundant.

## Evidence required for completion

- valid `SKILL.md` frontmatter and metadata for all five skills
- diff review showing each skill covers a distinct SCIR workflow
- validator output for each new skill
- repo validation outcome recorded in the completion update

## Completion evidence

- Added `.codex/skills/scir-spec-sync/`, `.codex/skills/scir-tier-profile-auditor/`, `.codex/skills/scir-lowering-provenance-check/`, `.codex/skills/scir-importer-boundary-auditor/`, and `.codex/skills/scir-benchmark-claim-auditor/`.
- Added `SKILL.md` plus `agents/openai.yaml` for each skill with distinct SCIR workflow triggers and output contracts.
- Ran `python C:/Users/Forre/.codex/skills/.system/skill-creator/scripts/quick_validate.py` for each new skill and all five passed.
- Regenerated `reports/exports/execution_queue.export.json` and `reports/exports/checkpoint_closeout.export.json` via `python scripts/build_execution_queue.py --mode write` so the queue/checkpoint exports matched the current governance sources.
- Ran `python scripts/run_repo_validation.py`; it passed after the export refresh, confirming the new skill directories did not introduce repo-validation drift.
