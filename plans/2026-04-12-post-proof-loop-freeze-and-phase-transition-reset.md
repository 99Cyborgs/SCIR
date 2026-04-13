# Post-proof-loop freeze and phase-transition reset

Status: complete
Owner: Codex
Date: 2026-04-12

## Objective

Freeze the current 11-case Python executable proof loop as the completed MVP corpus, replace the stale promotion-focused active item with a consolidation/reset item, and harden repo-contract enforcement so future widening or support-lane promotion cannot happen silently.

## Scope

- replace the completed Python promotion slice with a post-proof-loop consolidation item in the active control surfaces
- record a new decision that Phase 2 is complete enough to freeze without auto-activating Rust, Wasm, or Track `C`
- tighten repo-contract checks around the frozen 11-case Python proof loop, empty Python importer-only set, retained Track `C` posture, Rust importer-first posture, and bounded helper-free Wasm posture
- keep existing commands, benchmark tracks, and retained support surfaces working exactly as they do now

## Non-goals

- widening Python beyond the current 11 executable cases
- activating Rust as an active round-trip or benchmark lane
- widening helper-free Wasm coverage
- promoting Track `C` into the default executable benchmark gate
- changing grammar, schemas, benchmark tracks, or public command contracts

## Touched files

- CURRENT_FOCUS.md
- BACKLOG.md
- IMPLEMENTATION_PLAN.md
- DECISION_REGISTER.md
- scripts/validate_repo_contracts.py

## Invariants that must remain true

- `SCIR-H` remains the only normative semantic authority
- `SCIR-L` remains derivative-only
- the active Python proof loop remains the fixed 11-case executable corpus
- Rust remains importer-first evidence only
- helper-free Wasm remains subset-bound and non-promoted for non-emittable Python cases
- Track `C` remains a retained non-default diagnostic pilot

## Risks

- freeze-policy wording can drift if control surfaces and repo-contract markers do not move together
- over-hardcoding the current corpus in repo contracts could break legitimate future widening unless the new decision path is explicit
- phase-sequencing text can become misleading if Phase 2 completion and Phase 3 non-activation are not stated plainly

## Validation steps

- python scripts/validate_repo_contracts.py --mode test
- python scripts/validate_repo_contracts.py --mode audit
- python scripts/benchmark_contract_dry_run.py --include-track-c-pilot
- python scripts/run_repo_validation.py
- python scripts/run_repo_validation.py --require-rust --include-track-c-pilot
- make validate

## Rollback strategy

If the new freeze enforcement proves too rigid or inconsistent with the retained support-lane docs, revert the control-surface reset and repo-contract hardening together, restore the previous active plan reference, and keep the proof-loop completion state documented only in the historical promotion plan.

## Evidence required for completion

- diff review showing the active focus/reset surfaces replaced the completed promotion item
- a new decision-register entry freezing the 11-case Python proof loop as the current MVP corpus
- repo-contract checks proving the frozen proof-loop and retained support-lane posture are now explicit
- successful sequential validation for the required commands

## Completion evidence

- `CURRENT_FOCUS.md` now points to this post-proof-loop reset plan instead of the completed class/try promotion slice, while preserving the same root active target: Python subset importer -> canonical `SCIR-H` -> validator hardening.
- `BACKLOG.md` now ranks the next moves explicitly as decision points rather than implicit widening, including Rust importer-first, bounded Wasm, retained Track `C`, and broader object/exception follow-ons.
- `IMPLEMENTATION_PLAN.md` now states that Phase 2 is complete enough to freeze at the fixed 11-case Python proof loop and that Phase 3 is not auto-activated.
- `DECISION_REGISTER.md` now records `DR-016`, freezing the 11-case Python executable proof loop as the current MVP corpus and requiring a new decision plus synchronized control-surface updates before future widening.
- `scripts/validate_repo_contracts.py` now enforces:
  - the frozen 11-case Python executable and benchmark case set
  - an empty Python importer-only case set
  - the frozen helper-free Wasm-emittable Python case set
  - retained Rust importer-first wording in `frontend/rust/IMPORT_SCOPE.md`
  - retained non-default Track `C` wording in `BENCHMARK_STRATEGY.md`
  - the new active plan and active-item markers for the post-proof-loop reset
- Sequential validation completed successfully on 2026-04-12:
  - `python scripts/validate_repo_contracts.py --mode test`
  - `python scripts/validate_repo_contracts.py --mode audit`
  - `python scripts/benchmark_contract_dry_run.py --include-track-c-pilot`
  - `python scripts/run_repo_validation.py`
  - `python scripts/run_repo_validation.py --require-rust --include-track-c-pilot`
  - `make validate`
- Observed validation outcomes:
  - repo-contract checker self-tests passed with 11 negative fixtures
  - bootstrap pipeline still reports compile/test evidence for 11 supported bootstrap cases
  - Track `A` passed with median SCIR/source ratio `1.5`
  - Track `B` passed with Tier `A` compile/test `1.0`
  - retained Track `C` remained non-default and `mixed` with `accepted_case_count = 10`, `boundary_only_case_count = 1`, and `repair_accept_rate = 0.9091`
  - Rust-inclusive validation continued to pass with Rust retained as importer-first evidence only
