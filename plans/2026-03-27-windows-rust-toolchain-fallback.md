# Windows Rust Toolchain Fallback For Validation

Status: complete
Owner: Codex
Date: 2026-03-27

## Objective

Make Rust validation and benchmark execution select a usable Windows toolchain when the active default is installed but unusable.

## Scope

- add a shared Rust toolchain resolution helper for validation scripts
- use the resolved toolchain for Rust reconstruction validation and Rust Track `D` benchmark compilation
- update the repo validation entrypoint to report selected toolchain state explicitly
- update operator-facing validation notes and active milestone evidence if the fix clears the blocker

## Non-goals

- changing SCIR semantics, tiers, profiles, or schemas
- mutating the user's global rustup default
- broadening Rust subset or benchmark scope

## Touched files

- `plans/2026-03-27-windows-rust-toolchain-fallback.md`
- `scripts/rust_toolchain.py`
- `scripts/run_repo_validation.py`
- `scripts/scir_bootstrap_pipeline.py`
- `VALIDATION.md`
- `plans/milestone_02b_python_expansion.md`

## Invariants that must remain true

- Rust fallback stays repo-local and subprocess-scoped
- Python validation behavior remains unchanged
- no SCIR semantic or doctrine claim is widened by the toolchain fix

## Risks

- fallback logic could mask a real Rust compile failure if it only checks probe commands
- validation and benchmark paths could diverge if not both routed through the shared helper

## Validation steps

- `python scripts/scir_bootstrap_pipeline.py --language rust --mode validate`
- `python scripts/benchmark_contract_dry_run.py`
- `python scripts/run_repo_validation.py`
- `python scripts/run_repo_validation.py --require-rust`

## Rollback strategy

Revert the shared toolchain helper and its call-site changes if the fallback masks real Rust pipeline failures or introduces inconsistent validation behavior.

## Evidence required for completion

- Rust validation passes on this machine without changing the global rustup default
- benchmark dry run uses the same selected toolchain path
- repo validation reports the selected toolchain or a precise skip/failure reason

## Completion evidence

- `scripts/rust_toolchain.py` now probes actual Rust subprocess usability, including a compile/link check via `cargo test --no-run`, instead of only checking PATH presence
- `python scripts/run_repo_validation.py` passed on `2026-03-27` and reported `skipped_unusable_toolchain` with a precise diagnosis covering both the unusable GNU default and the missing `link.exe` for the MSVC fallback
- `python scripts/run_repo_validation.py --require-rust` failed on `2026-03-27` with the same precise toolchain diagnosis instead of surfacing misleading Rust reconstruction failures
- `python scripts/scir_bootstrap_pipeline.py --language rust --mode validate` now fails fast on `2026-03-27` with an explicit usable-toolchain error instead of reporting false SCIR reconstruction defects
- `python scripts/benchmark_contract_dry_run.py` now fails fast on `2026-03-27` with an explicit Rust Track `D` toolchain-unavailable message instead of a benchmark self-test setup failure
