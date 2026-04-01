# Autonomous Execution Queue

Status: complete
Owner: Codex
Date: 2026-03-27

## Objective

Add a canonical, low-touch execution queue that turns the current roadmap into an agent-consumable ordered work surface without changing milestone sequencing or semantic scope.

## Scope

- add a root execution-queue markdown contract
- add a derived JSON export for agent consumption
- add a generator and validation path for queue drift
- update root governance and validation docs so the queue is part of the repository contract

## Non-goals

- changing milestone ordering
- widening executable lowering, reconstruction, or benchmark scope
- introducing a new semantic authority outside the existing roadmap documents

## Touched files

- `EXECUTION_QUEUE.md`
- `schemas/execution_queue.schema.json`
- `reports/exports/execution_queue.export.json`
- `scripts/build_execution_queue.py`
- `scripts/validate_repo_contracts.py`
- `README.md`
- `REPO_MAP.md`
- `docs/repository_map.md`
- `VALIDATION.md`
- `VALIDATION_STRATEGY.md`
- `reports/README.md`
- `DECISION_REGISTER.md`

## Invariants that must remain true

- `IMPLEMENTATION_PLAN.md` remains the ordering authority
- Milestone 02B remains the active near-term queue source
- importer-only Python expansion does not imply executable downstream scope
- blocked witness work must point to explicit open questions
- derived exports remain mechanically derivable from their markdown source

## Risks

- queue language could accidentally imply executable scope creep
- export drift could create a second unsynchronized queue
- validation could become too keyword-fragile if the contract is underspecified

## Validation steps

- `python scripts/build_execution_queue.py --mode check`
- `python scripts/validate_repo_contracts.py --mode test`
- `python scripts/run_repo_validation.py`

## Rollback strategy

Remove the execution queue artifact, export, and validator hooks together; revert the decision-register entry and documentation updates so the repo returns to milestone-only governance.

## Evidence required for completion

- checked-in queue markdown and export agree
- repo checker rejects queue drift and scope-widening negative fixtures
- validation docs mention the execution queue explicitly
- decision register records the queue contract
