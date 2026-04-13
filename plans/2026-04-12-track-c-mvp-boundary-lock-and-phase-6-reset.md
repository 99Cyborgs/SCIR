# Track C MVP Boundary Lock and Phase-6 Reset

Status: complete
Owner: Codex
Date: 2026-04-12

## Objective

Resolve the remaining benchmark-lane ambiguity in favor of the current default: Track `C` remains a retained non-default diagnostic pilot for the remainder of the MVP and is not the next automatic benchmark phase after the frozen Python proof loop.

## Scope

- update roadmap/control surfaces so Phase 6 is no longer implied to auto-activate
- tighten benchmark doctrine and track-index wording so Track `C` is consistently described as retained non-default MVP support only
- add a new decision-register entry that locks Track `C` to retained non-default MVP posture
- extend benchmark metadata and repo-contract checks so silent Track `C` promotion requires a fresh decision and synchronized control-surface updates

## Non-goals

- no benchmark-track activation changes
- no Track `C` sample regeneration
- no benchmark schema changes
- no Python, Rust, or Wasm scope widening
- no change to Track `A` or Track `B` executable status

## Touched files

- CURRENT_FOCUS.md
- BACKLOG.md
- IMPLEMENTATION_PLAN.md
- DECISION_REGISTER.md
- BENCHMARK_STRATEGY.md
- benchmarks/tracks.md
- scripts/benchmark_contract_metadata.py
- scripts/validate_repo_contracts.py

## Invariants that must remain true

- the 11-case Python proof loop remains the frozen MVP executable corpus
- Track `A` and Track `B` remain the only active executable benchmark tracks
- Track `C` remains non-default, with `c_opaque_call` boundary-accounting-only
- Rust remains importer-first support only and Wasm remains bounded retained backend support only

## Risks

- changing benchmark posture wording without syncing metadata and repo-contract markers would create a new drift loop
- over-tightening Track `C` wording could accidentally contradict the existing opt-in pilot command surface

## Validation steps

- python scripts/validate_repo_contracts.py --mode test
- python scripts/validate_repo_contracts.py --mode audit
- python scripts/benchmark_contract_dry_run.py --include-track-c-pilot
- python scripts/run_repo_validation.py
- python scripts/run_repo_validation.py --require-rust --include-track-c-pilot
- make validate

## Rollback strategy

Revert the Track `C` roadmap/benchmark wording and repo-contract changes together if the updated freeze markers contradict the current opt-in pilot contract or break the existing validation path.

## Evidence required for completion

- diff review confirmed Track `C` roadmap, benchmark doctrine, benchmark metadata, and repo-contract surfaces all describe the same retained non-default MVP posture
- `python scripts/validate_repo_contracts.py --mode test`
- `python scripts/validate_repo_contracts.py --mode audit`
- `python scripts/benchmark_contract_dry_run.py --include-track-c-pilot`
- `python scripts/run_repo_validation.py`
- `python scripts/run_repo_validation.py --require-rust --include-track-c-pilot`
- `make validate`
