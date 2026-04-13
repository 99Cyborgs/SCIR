# MVP Completion and Pre-Baseline Alignment

Status: complete
Owner: Codex
Date: 2026-04-13

## Objective

Finish the current SCIR MVP implementation lane so the frozen 11-case Python proof loop, validator stack, retained support lanes, and benchmark doctrine describe one honest pre-baseline state.

## Scope

- remove truth-surface drift that still underclaims or mislabels executable proof-loop support
- harden repo-contract validation so the frozen 11-case executable subset cannot silently drift back toward importer-only wording
- fix the retained Rust pipeline self-test regression and wire the stronger Rust-inclusive validation path to exercise it
- keep retained Rust, Wasm, and Track `C` surfaces stable without widening their scope

## Non-goals

- no new Python fixture admissions
- no new frontend or backend activation
- no Rust, Wasm, or Track `C` promotion
- no schema redesign or benchmark-track expansion
- no new semantic constructs outside the already admitted executable subset

## Touched files

- README.md
- SYSTEM_BOUNDARY.md
- CURRENT_FOCUS.md
- plans/2026-04-13-mvp-completion-and-pre-baseline-alignment.md
- specs/scir_h_spec.md
- specs/validator_invariants.md
- SPEC_COMPLETENESS_CHECKLIST.md
- VALIDATION_STRATEGY.md
- docs/project_overview.md
- frontend/python/IMPORT_SCOPE.md
- frontend/python/AGENTS.md
- tests/README.md
- scripts/validate_repo_contracts.py
- scripts/python_importer_conformance.py
- scripts/scir_h_bootstrap_model.py
- scripts/run_repo_validation.py
- scripts/scir_bootstrap_pipeline.py

## Invariants that must remain true

- `SCIR-H` remains the only normative semantic authority
- `SCIR-L` remains derivative-only and subset-bound
- the executable Python proof loop remains frozen at 11 cases
- unsupported and deferred Python object and exception semantics remain explicit
- retained Rust, bounded Wasm, and retained Track `C` remain non-promoted support lanes

## Risks

- tightening truth-surface enforcement could expose more stale wording than expected
- strengthening Rust-inclusive validation must not accidentally make the default gate require a Rust toolchain
- spec wording changes must stay within the already implemented subset and avoid widening the admitted boundary

## Validation steps

- python scripts/validate_repo_contracts.py --mode test
- python scripts/python_importer_conformance.py --mode test
- python scripts/scir_bootstrap_pipeline.py --mode test
- python scripts/scir_bootstrap_pipeline.py --language rust --mode test
- python scripts/run_repo_validation.py
- python scripts/run_repo_validation.py --require-rust
- make validate

## Rollback strategy

Revert the truth-surface alignment and validation-hardening changes together if they contradict the frozen 11-case corpus contract or make the default gate depend on support-lane requirements it previously did not have.

## Evidence required for completion

- diff review shows specs, docs, fixtures, and validators agree on the frozen 11-case executable subset
- `python scripts/validate_repo_contracts.py --mode test`
- `python scripts/python_importer_conformance.py --mode test`
- `python scripts/scir_bootstrap_pipeline.py --mode test`
- `python scripts/scir_bootstrap_pipeline.py --language rust --mode test`
- `python scripts/run_repo_validation.py`
- `python scripts/run_repo_validation.py --require-rust`
- `make validate`

## Completion evidence

- diff review shows README, SYSTEM_BOUNDARY, and supporting overview docs now state the same bounded comparison-ready MVP boundary as the executable gate
- `python scripts/validate_repo_contracts.py --mode test` passed; repository checker self-tests passed with 25 negative fixtures
- `python scripts/python_importer_conformance.py --mode test` passed; Python importer self-tests passed with 15 negative fixtures
- `python scripts/scir_bootstrap_pipeline.py --mode test` passed; Python pipeline self-tests passed
- `python scripts/scir_bootstrap_pipeline.py --language rust --mode test` passed after fixing the retained Rust self-test harness
- `python scripts/run_repo_validation.py` passed
- `python scripts/run_repo_validation.py --require-rust` passed and now exercised the retained Rust pipeline self-tests
- `python scripts/validate_repo_contracts.py --mode audit` passed
- `make validate` passed
