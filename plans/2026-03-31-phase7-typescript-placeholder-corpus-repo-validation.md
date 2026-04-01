# Phase 7 TypeScript Placeholder Corpus Repository Validation

Status: complete
Owner: Codex
Date: 2026-03-31

## Objective

Complete `Q-07-010` by making repository-contract validation reject drift in the fully materialized dormant TypeScript placeholder corpus and advance the queue to the future `validate-fixtures` activation slice.

## Scope

- add explicit dormant TypeScript placeholder-corpus checks to `scripts/validate_repo_contracts.py`
- extend repository-checker self-tests to cover TypeScript placeholder file-shape and report-contract drift
- update validation and milestone doctrine so repository validation explicitly owns dormant TypeScript corpus enforcement until the language-local checker exists
- mark `Q-07-010` complete and queue `Q-07-011` as the next ready item
- regenerate the execution queue export from the updated queue markdown

## Non-goals

- activating `scripts/typescript_importer_conformance.py`
- adding live TypeScript importer behavior
- adding executable `D-JS`, `SCIR-L`, translation, reconstruction, or benchmark artifacts
- changing schemas or public report formats

## Touched files

- `plans/2026-03-31-phase7-typescript-placeholder-corpus-repo-validation.md`
- `scripts/validate_repo_contracts.py`
- `VALIDATION_STRATEGY.md`
- `tests/README.md`
- `plans/milestone_07_typescript_witness_slice.md`
- `EXECUTION_QUEUE.md`
- `reports/exports/execution_queue.export.json`

## Invariants that must remain true

- the first Phase 7 TypeScript slice remains dormant, importer-only, and non-executable
- admitted TypeScript placeholder bundles continue to require canonical `SCIR-H`
- rejected TypeScript placeholder bundles continue to omit canonical `SCIR-H`
- repository validation enforces the placeholder corpus contract without claiming live TypeScript conformance

## Risks

- overly loose repository checks could let the published admitted-vs-rejected corpus contract drift silently
- overly specific repository checks could hard-code placeholder prose instead of stable contract fields and boundary markers

## Validation steps

- `python scripts/build_execution_queue.py --mode write`
- `python scripts/build_execution_queue.py --mode check`
- `python scripts/validate_repo_contracts.py --mode validate`
- `python scripts/validate_repo_contracts.py --mode test`
- `python scripts/run_repo_validation.py`

## Rollback strategy

Revert the repository-checker, doctrine, and queue changes together if the new enforcement proves inconsistent with the published dormant TypeScript corpus contract or accidentally activates live importer expectations.

## Evidence required for completion

- repository validation rejects dormant TypeScript placeholder corpus drift in case IDs, file sets, and placeholder report posture
- repository-checker self-tests include TypeScript-specific negative fixtures and report a derived fixture count
- validation doctrine explicitly assigns dormant TypeScript corpus enforcement to repository validation until the language-local checker exists
- `Q-07-010` is marked complete, `Q-07-011` is the next ready item, and the checked-in execution queue export is synchronized
- validation commands pass

## Completion evidence

- `scripts/validate_repo_contracts.py` now enforces the fixed nine-case dormant TypeScript placeholder corpus contract, including exact admitted-vs-rejected file sets, rejected-case `expected.scirh` absence, placeholder report posture, and non-live diagnostic markers
- repository-checker self-tests now include TypeScript-specific negative fixtures for rejected-case file-shape drift and rejected manifest-tier drift, and the self-test success message now derives its fixture count from the registered case list
- `VALIDATION_STRATEGY.md`, `tests/README.md`, and `plans/milestone_07_typescript_witness_slice.md` now state that repository validation actively enforces the dormant TypeScript placeholder corpus shape until the language-local checker exists
- `EXECUTION_QUEUE.md` now marks `Q-07-010` complete and makes `Q-07-011` the first ready item; `reports/exports/execution_queue.export.json` was regenerated from queue markdown
- `python scripts/build_execution_queue.py --mode write` passed on `2026-03-31`
- `python scripts/build_execution_queue.py --mode check` passed on `2026-03-31`
- `python scripts/validate_repo_contracts.py --mode validate` passed on `2026-03-31`
- `python scripts/validate_repo_contracts.py --mode test` passed on `2026-03-31`
- `python scripts/run_repo_validation.py` passed on `2026-03-31`
