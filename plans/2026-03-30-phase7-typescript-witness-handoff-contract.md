# Phase 7 TypeScript Witness Handoff Contract

Status: complete
Owner: Codex
Date: 2026-03-30

## Objective

Make the first Phase 7 TypeScript witness slice decision-complete as a doctrine-only planning handoff without admitting executable `D-JS`, lowering, reconstruction, or benchmark scope.

## Scope

- narrow the active Phase 7 milestone to the first admissible TypeScript interface-shaped witness slice
- update TypeScript importer doctrine so interfaces are the only admitted witness-bearing surface for the first Phase 7 step
- update validator and runtime doctrine so future witness work has explicit non-executable blocking conditions
- keep OQ-018 and OQ-019 open while turning their defaults into operational planning constraints
- advance the execution queue to the next bounded Phase 7 item after the handoff contract is recorded

## Non-goals

- implementing a TypeScript importer
- adding executable `D-JS` lowering, reconstruction, or benchmarks
- changing schemas, `SCIR-L` op semantics, or backend tracks
- resolving OQ-018 or OQ-019 permanently

## Touched files

- `plans/2026-03-30-phase7-typescript-witness-handoff-contract.md`
- `plans/milestone_07_typescript_witness_slice.md`
- `frontend/typescript/IMPORT_SCOPE.md`
- `VALIDATION_STRATEGY.md`
- `validators/validator_contracts.md`
- `docs/runtime_doctrine.md`
- `OPEN_QUESTIONS.md`
- `EXECUTION_QUEUE.md`
- `reports/exports/execution_queue.export.json`

## Invariants that must remain true

- Phase 7 remains doctrine-only and non-executable
- TypeScript interfaces are the only admitted witness-bearing surface for the first Phase 7 step
- `D-JS` remains blocked on explicit lowering, validation, reconstruction, and benchmark gates

## Risks

- broad candidate-scope wording could still imply that classes or async behavior are already admitted
- queue updates could accidentally imply executable TypeScript work before downstream contracts exist

## Validation steps

- `python scripts/build_execution_queue.py --mode check`
- `python scripts/validate_repo_contracts.py --mode validate`
- `python scripts/run_repo_validation.py`

## Rollback strategy

Revert the Phase 7 doctrine, open-question default, and queue updates together if the handoff wording accidentally widens executable scope or leaves the next queue item ambiguous.

## Evidence required for completion

- the active Phase 7 milestone names a bounded interface-shaped witness slice and explicit non-goals
- TypeScript import scope and validator/runtime doctrine agree that the first slice is importer-only and non-executable
- OQ-018 and OQ-019 defaults are specific enough to guide the next implementation slice without closing the questions
- the queue marks `Q-07-001` complete and names the next bounded Phase 7 item

## Completion evidence

- `plans/milestone_07_typescript_witness_slice.md` now names the first admitted Phase 7 slice as interface-shaped, module-local, planning-only, and importer-only
- `frontend/typescript/IMPORT_SCOPE.md`, `VALIDATION_STRATEGY.md`, `validators/validator_contracts.md`, and `docs/runtime_doctrine.md` now agree that the first Phase 7 slice is non-executable and does not admit functions, async behavior, classes, or prototype semantics
- `OPEN_QUESTIONS.md` and `reports/exports/open_questions.export.json` now make the OQ-018 and OQ-019 defaults operational for the first TypeScript witness slice
- `EXECUTION_QUEUE.md` and `reports/exports/execution_queue.export.json` now record the completed handoff and the next bounded Phase 7 item
- `python scripts/build_execution_queue.py --mode check` passed on `2026-03-30`
- `python scripts/validate_repo_contracts.py --mode validate` passed on `2026-03-30`
- `python scripts/run_repo_validation.py` passed on `2026-03-30`
