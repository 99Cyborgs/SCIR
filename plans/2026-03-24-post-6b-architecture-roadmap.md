# Post-6B Architecture Roadmap

Status: complete
Owner: Codex
Date: 2026-03-24

## Objective

Make the post-6B architecture roadmap explicit without widening executable semantics: promote Python Milestone 02B as the active near-term expansion track, define the next new phase as witness-bearing second-language evidence, and lock the default candidate to TypeScript interface-shaped witnesses.

## Scope

- extend the normative implementation roadmap beyond Phase 6B
- promote Milestone 02B from proposed follow-on work to the active near-term architecture milestone
- record the default Phase 7 candidate slice as TypeScript interface-shaped witness evidence
- tighten validator and runtime doctrine so importer-only expansion and non-executable `D-JS` claims stay explicit
- narrow the open witness-roadmap question into concrete unresolved contract questions

## Non-goals

- adding executable `D-JS` support
- widening the canonical `SCIR-L` opcode surface
- introducing a new backend track
- implementing Python 02B constructs or TypeScript witness execution

## Touched files

- `IMPLEMENTATION_PLAN.md`
- `plans/milestone_02b_python_expansion.md`
- `ARCHITECTURE.md`
- `SYSTEM_BOUNDARY.md`
- `VALIDATION_STRATEGY.md`
- `validators/validator_contracts.md`
- `docs/runtime_doctrine.md`
- `frontend/typescript/IMPORT_SCOPE.md`
- `BENCHMARK_STRATEGY.md`
- `README.md`
- `DECISION_REGISTER.md`
- `OPEN_QUESTIONS.md`
- `reports/exports/decision_register.export.json`
- `reports/exports/open_questions.export.json`

## Invariants that must remain true

- `SCIR-H` remains the semantic source of truth
- `SCIR-L` remains derivative and does not gain `L`-only semantics
- Python Milestone 02B importer acceptance does not imply executable lowering, reconstruction, or benchmark participation
- `D-JS` remains doctrine-only until a later milestone publishes executable downstream contracts
- no new backend track is introduced by the roadmap update

## Risks

- roadmap language could accidentally imply executable TypeScript support
- Python 02B could look broader than fixture-backed importer evidence
- validator doctrine could drift if post-6B constraints are recorded only in planning docs

## Validation steps

- `python scripts/validate_repo_contracts.py --mode validate`
- `python scripts/run_repo_validation.py`

## Rollback strategy

Remove the post-6B roadmap additions, restore Milestone 02B to proposed-only status, and revert the new decision/open-question narrowing if the doctrine cannot stay aligned without implying unsupported executable scope.

## Evidence required for completion

- implementation roadmap includes an explicit post-6B phase and near-term milestone note
- decision register fixes the post-6B sequencing
- open questions are narrowed to unresolved witness-slice contract questions
- validator and runtime doctrine explicitly reject executable `D-JS` scope creep
- repo contract validation passes
