# Rust MVP boundary lock and OQ-003 resolution

Status: complete
Owner: Codex
Date: 2026-04-12

## Objective

Resolve `OQ-003` in favor of the current default by locking Rust to importer-first evidence for the remainder of the MVP, removing the remaining roadmap ambiguity about Rust activation, and hardening repo-contract checks so Rust cannot silently re-enter active round-trip, backend, or benchmark scope.

## Scope

- add one new decision-register entry resolving the Rust MVP scope question
- remove `OQ-003` from `OPEN_QUESTIONS.md`
- align active control and roadmap surfaces so Rust is described consistently as a retained support lane, not an implied next active phase
- tighten repo-contract enforcement around Rust importer-first posture and against silent Rust benchmark or active-phase promotion

## Non-goals

- activating Rust round-trip, reconstruction, backend, or benchmark claims
- adding new Rust fixtures or changing Rust importer semantics
- widening helper-free Wasm or benchmark tracks
- changing Python proof-loop scope

## Touched files

- CURRENT_FOCUS.md
- BACKLOG.md
- IMPLEMENTATION_PLAN.md
- DECISION_REGISTER.md
- OPEN_QUESTIONS.md
- ARCHITECTURE.md
- SYSTEM_BOUNDARY.md
- README.md
- BENCHMARK_STRATEGY.md
- frontend/rust/IMPORT_SCOPE.md
- scripts/validate_repo_contracts.py

## Invariants that must remain true

- `SCIR-H` remains the only normative semantic authority
- Python remains the active implementation lane
- Rust remains importer-first evidence only for the MVP
- helper-free Wasm remains subset-bound and non-promoted
- Track `C` remains non-default

## Risks

- roadmap text may still imply Rust is the next automatic phase if the wording is not synchronized across root docs
- repo-contract hardening can become too narrow if it keys on one phrase instead of the actual boundary posture
- removing `OQ-003` without a clear decision entry would hide rather than resolve the ambiguity

## Validation steps

- python scripts/validate_repo_contracts.py --mode test
- python scripts/validate_repo_contracts.py --mode audit
- python scripts/rust_importer_conformance.py --mode validate-fixtures
- python scripts/benchmark_contract_dry_run.py --include-track-c-pilot
- python scripts/run_repo_validation.py --require-rust --include-track-c-pilot
- make validate

## Rollback strategy

If the Rust boundary lock causes inconsistency with the current roadmap or support-lane docs, revert the decision/control-surface changes and the repo-contract additions together, restore `OQ-003`, and keep Rust scoped only by the previous post-proof-loop reset until a better-aligned decision slice is prepared.

## Evidence required for completion

- diff review showing `OQ-003` was replaced by an explicit Rust MVP boundary decision
- root docs, roadmap docs, and `frontend/rust/IMPORT_SCOPE.md` all describing the same importer-first Rust posture
- repo-contract checks proving Rust active-phase, backend, and benchmark promotion cannot drift in silently
- successful sequential validation for the required commands

## Completion evidence

- `OQ-003` has been removed from `OPEN_QUESTIONS.md`, and `DECISION_REGISTER.md` now records `DR-017`, resolving Rust scope in favor of importer-first MVP evidence only.
- `CURRENT_FOCUS.md`, `BACKLOG.md`, `IMPLEMENTATION_PLAN.md`, `SYSTEM_BOUNDARY.md`, `README.md`, `ARCHITECTURE.md`, `BENCHMARK_STRATEGY.md`, and `frontend/rust/IMPORT_SCOPE.md` now describe the same Rust posture:
  - Rust is preserved and validated as importer-first support
  - Rust is not the next automatic active phase after the frozen Python proof loop
  - Rust remains outside active round-trip, backend, and benchmark claims for the MVP
- `scripts/validate_repo_contracts.py` now enforces:
  - the new active plan reference for the Rust boundary-lock slice
  - the resolved Rust phase-freeze markers in `IMPLEMENTATION_PLAN.md`
  - the importer-first Rust scope markers in `frontend/rust/IMPORT_SCOPE.md`
  - the explicit Rust benchmark-freeze marker in `BENCHMARK_STRATEGY.md`
  - the absence of `OQ-003` from `OPEN_QUESTIONS.md`
  - `DR-017` and its Rust MVP boundary text in `DECISION_REGISTER.md`
- Sequential validation completed successfully on 2026-04-12:
  - `python scripts/validate_repo_contracts.py --mode test`
  - `python scripts/validate_repo_contracts.py --mode audit`
  - `python scripts/rust_importer_conformance.py --mode validate-fixtures`
  - `python scripts/benchmark_contract_dry_run.py --include-track-c-pilot`
  - `python scripts/run_repo_validation.py --require-rust --include-track-c-pilot`
  - `make validate`
- Observed validation outcomes:
  - repo-contract checker self-tests passed with 15 negative fixtures
  - Rust importer fixture validation passed unchanged
  - benchmark dry run still passed with Track `C` retained as a non-default diagnostic pilot
  - Rust-inclusive repository validation still passed with Rust as importer-first evidence only
