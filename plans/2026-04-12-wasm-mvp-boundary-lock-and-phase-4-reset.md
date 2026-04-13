# Wasm MVP Boundary Lock and Phase-4 Reset

Status: complete
Owner: Codex
Date: 2026-04-12

## Objective

Resolve the remaining Wasm roadmap ambiguity in favor of the current default: helper-free Wasm remains a bounded retained support lane for the remainder of the MVP and is not the next automatic implementation phase after the frozen Python proof loop.

## Scope

- update root control surfaces so they stop implying Phase 4 Wasm auto-activation
- tighten Wasm boundary wording in backend, profile, preservation, and benchmark docs
- add a new decision-register entry that locks Wasm to retained bounded MVP support
- extend repo-contract checks and self-tests so silent Wasm promotion requires a fresh decision and synchronized control-surface updates

## Non-goals

- no Wasm backend widening
- no new backend fixtures or emitted modules
- no schema changes
- no benchmark-track activation changes
- no Rust, Python, or Track `C` scope widening

## Touched files

- CURRENT_FOCUS.md
- BACKLOG.md
- IMPLEMENTATION_PLAN.md
- DECISION_REGISTER.md
- BENCHMARK_STRATEGY.md
- README.md
- ARCHITECTURE.md
- docs/target_profiles.md
- docs/preservation_contract.md
- backends/README.md
- backends/wasm/README.md
- scripts/validate_repo_contracts.py
- scripts/wasm_backend_metadata.py

## Invariants that must remain true

- the 11-case Python proof loop remains the frozen MVP executable corpus
- helper-free Wasm remains bounded to the existing scalar slice plus the fixed Rust record-cell ABI slice
- Wasm stays outside active benchmark claims and does not imply native or host parity
- Track `C` remains non-default and Rust remains importer-first support only

## Risks

- changing wording in backend/profile docs without syncing the repo-contract checker would create a new drift loop
- tightening the Wasm boundary too aggressively could accidentally contradict the still-supported emitted-module slice

## Validation steps

- python scripts/validate_repo_contracts.py --mode test
- python scripts/validate_repo_contracts.py --mode audit
- python scripts/benchmark_contract_dry_run.py --include-track-c-pilot
- python scripts/run_repo_validation.py
- python scripts/run_repo_validation.py --require-rust --include-track-c-pilot
- make validate

## Rollback strategy

Revert the Wasm boundary-lock wording and repo-contract changes together if the updated markers contradict executable metadata or break the existing retained helper-free Wasm validation path.

## Evidence required for completion

- diff review confirmed the control-plane reset plus one truth-restoring Wasm README sync: `backends/wasm/README.md` now includes `fixture.python_importer.b_if_else_return`, matching `scripts/wasm_backend_metadata.py`
- `python scripts/validate_repo_contracts.py --mode test`
- `python scripts/validate_repo_contracts.py --mode audit`
- `python scripts/benchmark_contract_dry_run.py --include-track-c-pilot`
- `python scripts/run_repo_validation.py`
- `python scripts/run_repo_validation.py --require-rust --include-track-c-pilot`
- `make validate`
