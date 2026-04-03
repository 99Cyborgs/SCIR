# Q-04-007 Define validator and preservation obligations for the candidate Wasm record-cell ABI

Status: complete
Owner: Codex
Date: 2026-04-02

## Objective

Specify the validator, lowering, and preservation-report obligations that would have to hold before the candidate Wasm record-cell ABI could become executable.

## Scope

- Define validation constraints for canonical field-order offsets, fixed `int`-field records, shared handle callers, and explicit non-support boundaries.
- Define preservation obligations and downgrade requirements for the candidate record-cell ABI.
- Record the obligations in governance and narrow the open question from “what obligations” to “whether bounded implementation is credible.”
- Advance the queue to the first bounded-implementation assessment slice.

## Non-goals

- No implementation of the candidate record-cell ABI.
- No admission of `field.addr` or any record-carrying Wasm execution path.
- No change to the current helper-free scalar executable Wasm subset.
- No new `SCIR-L` ops or schema changes.

## Touched files

- VALIDATION_STRATEGY.md
- LOWERING_CONTRACT.md
- docs/preservation_contract.md
- DECISION_REGISTER.md
- OPEN_QUESTIONS.md
- EXECUTION_QUEUE.md
- reports/exports/open_questions.export.json
- reports/exports/decision_register.export.json
- reports/exports/execution_queue.export.json
- plans/2026-04-02-q-04-007-define-record-cell-abi-validator-and-preservation.md
- plans/2026-04-01-mvp-narrowing-and-contract-hardening.md

## Invariants that must remain true

- The current helper-free scalar Wasm subset remains the only executable backend surface.
- Candidate record-cell ABI work remains design-track doctrine only.
- Wasm claims remain profile `P` and must not imply native or host parity.
- Non-candidate record, host, imported-memory, async, opaque, and broader call shapes remain explicitly unsupported.

## Risks

- The obligations could accidentally imply executable support instead of preconditions for future work.
- Preservation language could overclaim beyond `P2`.
- The narrowed next-step question could still be too broad to guide implementation assessment.

## Validation steps

- python scripts/build_execution_queue.py --mode check
- python scripts/validate_repo_contracts.py --mode validate
- python scripts/validate_repo_contracts.py --mode test
- python scripts/run_repo_validation.py

## Rollback strategy

Revert the validation-doctrine, preservation-doctrine, decision-register, open-question, and queue updates together if the obligation set does not stay clearly pre-executable and subset-bound.

## Evidence required for completion

- Validation doctrine names the candidate record-cell ABI preconditions explicitly.
- Preservation doctrine names the required downgrade/reporting posture explicitly.
- The open question is narrowed from “what obligations” to “whether bounded implementation is credible.”
- `Q-04-007` is closed, the next queue slice assesses bounded implementation credibility, and exports are synchronized.
