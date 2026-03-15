# PLANS
Status: Normative

Use this template for any work that crosses files, semantics, validators, schemas, or benchmark doctrine.

## When a plan is mandatory

A plan is mandatory when work:

- touches 3 or more files,
- changes `specs/`,
- changes `schemas/`,
- changes validator behavior,
- changes target profiles, preservation levels, feature tiers, or unsupported cases,
- changes benchmark tracks, baselines, gates, or contamination controls,
- adds a new tool contract or directory.

## Plan template

```markdown
# <plan title>

Status: proposed | in-progress | blocked | complete
Owner:
Date:

## Objective

## Scope

## Non-goals

## Touched files

- path
- path

## Invariants that must remain true

- invariant
- invariant

## Risks

- risk
- risk

## Validation steps

- command
- command

## Rollback strategy

## Evidence required for completion

- report
- benchmark
- diff review
```

## Completion rule

A plan is complete only when its evidence section is satisfied and the relevant decision register or open-questions updates have been made.
