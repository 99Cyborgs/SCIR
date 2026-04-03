# 2026-04-01 Q-04-001 Lock the Wasm MVP Contract to the Bounded Derivative Subset

Status: complete
Owner: Codex
Date: 2026-04-01

## Objective

Keep the helper-free Wasm reference backend aligned to the already-bounded derivative subset without widening backend semantics, emitted cases, or parity claims.

## Scope

- export one authoritative Wasm backend metadata contract for admitted emitted cases, lowering rules, report shape, and non-emittable rules
- derive Wasm-emittable Python and Rust case lists plus report strings from that metadata
- make the Wasm README, lowering contract, and validation strategy expose machine-checkable backend lists
- add repository drift checks and negative self-tests for the Wasm backend contract
- close out `Q-04-001` and advance the execution queue to the benchmark phase handoff

## Non-goals

- no new Wasm-emittable source shapes
- no helper imports, runtime shims, or linear-memory conventions
- no schema changes
- no native, JS host, or broader backend parity claims

## Touched files

- `backends/wasm/README.md`
- `LOWERING_CONTRACT.md`
- `VALIDATION_STRATEGY.md`
- `scripts/wasm_backend_metadata.py`
- `scripts/scir_bootstrap_pipeline.py`
- `scripts/validate_repo_contracts.py`
- `EXECUTION_QUEUE.md`
- `reports/exports/execution_queue.export.json`
- `plans/2026-04-01-mvp-narrowing-and-contract-hardening.md`

## Invariants that must remain true

- helper-free Wasm remains profile `P` with a `P2` ceiling
- emitted cases remain `fixture.python_importer.a_basic_function` and `fixture.rust_importer.a_mut_local` only
- `field.addr`, direct call, async, and opaque lowering remain non-emittable
- Wasm reporting remains path-qualified under `l_to_wasm`
- Wasm wording does not imply native or host-runtime parity

## Risks

- backend assumptions are currently duplicated across docs and emitter code, so drift checks must target exact lists instead of prose fragments
- moving case ownership into a shared Wasm contract can accidentally desynchronize Python/Rust case metadata if not validated explicitly
- queue closeout can drift if the markdown and export are not regenerated together

## Validation steps

- `python scripts/validate_repo_contracts.py --mode validate`
- `python scripts/validate_repo_contracts.py --mode test`
- `python scripts/scir_bootstrap_pipeline.py --mode validate`
- `python scripts/scir_bootstrap_pipeline.py --language rust --mode validate`
- `python scripts/build_execution_queue.py --mode check`
- `python scripts/run_repo_validation.py`
- `python scripts/run_repo_validation.py --require-rust`

## Rollback strategy

Revert the shared Wasm metadata module, emitter/checker derivation, Wasm doc drift checks, and queue/export updates as one unit if the helper-free Wasm subset cannot stay coherent under validation.

## Evidence required for completion

- one authoritative Wasm backend metadata contract exists on disk
- emitter case lists and report strings derive from that metadata
- repository validation fails on drift between Wasm metadata and backend doctrine docs
- `Q-04-001` is closed, the queue export is synchronized, and both default and Rust-required validation paths pass

## Completion evidence

- `scripts/wasm_backend_metadata.py` is now the authoritative Wasm backend contract for emitted Python and Rust modules, admitted lowering rules, non-emittable lowering rules, and `l_to_wasm` report strings
- `scripts/scir_bootstrap_pipeline.py` now derives Python and Rust Wasm-emittable case lists plus Wasm preservation-report strings from that metadata and rejects lowering rules outside the admitted Wasm contract
- `backends/wasm/README.md`, `LOWERING_CONTRACT.md`, and `VALIDATION_STRATEGY.md` now expose machine-checkable Wasm module and lowering-rule lists that repository validation compares directly against `WASM_BACKEND_METADATA`
- `scripts/validate_repo_contracts.py` now fails on Wasm drift across backend doctrine docs and the checked-in `reports/examples/preservation_l_to_wasm.example.json`, and it has negative self-tests for emitted-module, lowering-rule, and validation-strategy drift
- `Q-04-001` is closed, `reports/exports/execution_queue.export.json` is synchronized, and the next ready slice is `Q-05-001`
