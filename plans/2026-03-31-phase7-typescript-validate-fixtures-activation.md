# Phase 7 TypeScript Validate-Fixtures Activation

Status: complete
Owner: Codex
Date: 2026-03-31

## Objective

Complete `Q-07-011` by activating `scripts/typescript_importer_conformance.py --mode validate-fixtures` for the dormant TypeScript placeholder corpus and wiring that check into the existing validation baseline without activating live importer execution.

## Scope

- implement real dormant-corpus integrity checks in `scripts/typescript_importer_conformance.py`
- keep `--mode test` reserved and explicitly non-live
- wire TypeScript `validate-fixtures` into `make validate` and `scripts/run_repo_validation.py`
- update command/doctrine docs so they describe the active `validate-fixtures` gate and the still-reserved `test` mode
- mark `Q-07-011` complete, queue `Q-07-012`, and regenerate the execution-queue export

## Non-goals

- adding live TypeScript importer behavior
- activating generated-vs-golden `test` mode
- adding executable `D-JS`, `SCIR-L`, translation, reconstruction, or benchmark artifacts
- changing schemas or public report formats

## Touched files

- `plans/2026-03-31-phase7-typescript-validate-fixtures-activation.md`
- `scripts/typescript_importer_conformance.py`
- `scripts/run_repo_validation.py`
- `Makefile`
- `README.md`
- `ci/validation_pipeline.md`
- `VALIDATION_STRATEGY.md`
- `tests/README.md`
- `tests/typescript_importer/README.md`
- `plans/milestone_07_typescript_witness_slice.md`
- `EXECUTION_QUEUE.md`
- `reports/exports/execution_queue.export.json`

## Invariants that must remain true

- the first Phase 7 TypeScript slice remains importer-only and non-executable
- admitted TypeScript placeholder cases keep non-canonical sentinel `expected.scirh` files
- rejected TypeScript placeholder cases continue to omit `expected.scirh`
- `--mode test` remains reserved and must not claim generated-vs-golden conformance

## Risks

- the TypeScript checker could accidentally overclaim canonical `SCIR-H` validation if it parses the admitted sentinel files
- command-contract docs could drift if the new validation step lands in wrappers without synchronized README and CI doctrine updates

## Validation steps

- `python scripts/typescript_importer_conformance.py --mode validate-fixtures`
- `python scripts/typescript_importer_conformance.py --mode test`
- `python scripts/build_execution_queue.py --mode write`
- `python scripts/build_execution_queue.py --mode check`
- `python scripts/validate_repo_contracts.py --mode validate`
- `python scripts/run_repo_validation.py`
- `make validate`

## Rollback strategy

Revert the TypeScript conformance-script activation and the associated wrapper/doc/queue updates together if the new checker implies live importer semantics, widens executable scope, or destabilizes the published validation command contract.

## Evidence required for completion

- `validate-fixtures` actively rejects dormant TypeScript placeholder corpus drift
- `--mode test` remains reserved and exits clearly as non-live
- `make validate` and `python scripts/run_repo_validation.py` invoke the TypeScript `validate-fixtures` gate
- docs describe `validate-fixtures` as active and `test` as reserved
- `Q-07-011` is complete, `Q-07-012` is ready, the queue export is synchronized, and validation commands pass

## Completion evidence

- `scripts/typescript_importer_conformance.py` now implements real dormant TypeScript `validate-fixtures` checks for the fixed nine-case placeholder corpus, including exact file sets, placeholder text markers, admitted sentinel `expected.scirh` markers, schema-valid JSON artifacts, and admitted-vs-rejected report posture
- `scripts/typescript_importer_conformance.py --mode test` now remains explicitly reserved and reports that `validate-fixtures` is active while generated-vs-golden conformance is still non-live
- `Makefile` and `scripts/run_repo_validation.py` now invoke the TypeScript `validate-fixtures` gate alongside the existing Python and Rust validation steps
- `README.md`, `ci/validation_pipeline.md`, `VALIDATION_STRATEGY.md`, `tests/README.md`, `tests/typescript_importer/README.md`, and `plans/milestone_07_typescript_witness_slice.md` now describe TypeScript `validate-fixtures` as active and `test` mode as still reserved
- `EXECUTION_QUEUE.md` now marks `Q-07-011` complete and makes `Q-07-012` the first ready item; `reports/exports/execution_queue.export.json` was regenerated from queue markdown
- `python scripts/typescript_importer_conformance.py --mode validate-fixtures` passed on `2026-03-31`
- `python scripts/typescript_importer_conformance.py --mode test` returned exit code `2` with the reserved non-live message on `2026-03-31`
- `python scripts/build_execution_queue.py --mode write` passed on `2026-03-31`
- `python scripts/build_execution_queue.py --mode check` passed on `2026-03-31`
- `python scripts/validate_repo_contracts.py --mode validate` passed on `2026-03-31`
- `python scripts/run_repo_validation.py` passed on `2026-03-31`
- `make validate` could not be executed in this environment because `make` is not installed; the equivalent underlying Python validation baseline was executed directly instead
