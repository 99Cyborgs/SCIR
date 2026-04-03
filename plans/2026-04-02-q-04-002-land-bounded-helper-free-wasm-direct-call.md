# 2026-04-02 Q-04-002 Land Bounded Helper-Free Wasm Direct-Call Emission

Status: complete
Owner: Codex
Date: 2026-04-02

## Objective

Admit the fixed Python `b_direct_call` shape into the helper-free Wasm backend without widening beyond the current bounded same-module scalar call case.

## Scope

- mark the fixed Python `b_direct_call` case as Wasm-emittable in the authoritative Python proof-loop metadata
- widen the Wasm backend metadata to admit bounded `H_DIRECT_CALL`
- implement helper-free WAT emission for the exact lowered `identity` / `call_identity` shape
- update Wasm doctrine and validation surfaces to reflect the widened bounded subset
- keep path-qualified `l_to_wasm` preservation reporting explicit for the widened module set

## Non-goals

- no support for imported calls, opaque calls, async calls, recursion, indirect calls, or broad call graphs
- no runtime helpers, shims, tables, or hidden host semantics
- no widening of Rust Wasm emission
- no benchmark or Track `C` policy change

## Touched files

- `scripts/scir_python_bootstrap.py`
- `scripts/wasm_backend_metadata.py`
- `scripts/scir_bootstrap_pipeline.py`
- `scripts/validate_repo_contracts.py`
- `backends/wasm/README.md`
- `LOWERING_CONTRACT.md`
- `VALIDATION_STRATEGY.md`
- `DECISION_REGISTER.md`
- `EXECUTION_QUEUE.md`
- `reports/exports/decision_register.export.json`
- `reports/exports/execution_queue.export.json`
- `plans/2026-04-01-mvp-narrowing-and-contract-hardening.md`

## Invariants that must remain true

- Wasm remains helper-free and subset-bound
- no native or host parity claim leaks in
- async, opaque, imported, and broader direct-call shapes remain non-emittable
- `l_to_wasm` reporting remains path-qualified with explicit profile `P` and `P2` ceiling
- the active Python proof loop remains the decisive end-to-end MVP path

## Risks

- allowing `H_DIRECT_CALL` too broadly could silently widen beyond the fixed same-module scalar call shape
- Wasm validation could stop distinguishing helper-free local direct calls from imported or opaque calls
- documentation drift could make the backend look broader than the executable emitter actually is

## Validation steps

- `python scripts/scir_bootstrap_pipeline.py --mode validate`
- `python scripts/scir_bootstrap_pipeline.py --mode test`
- `python scripts/validate_repo_contracts.py --mode validate`
- `python scripts/validate_repo_contracts.py --mode test`
- `python scripts/build_execution_queue.py --mode write`
- `python scripts/build_execution_queue.py --mode check`
- `python scripts/run_repo_validation.py`

## Rollback strategy

Revert the direct-call Wasm admission, emitter changes, backend metadata updates, and doctrine/export updates as one unit if bounded same-module scalar calls cannot stay helper-free and subset-bound.

## Evidence required for completion

- `fixture.python_importer.b_direct_call` is either helper-free Wasm-emittable with executable evidence or remains explicitly blocked for a concrete bounded reason
- Wasm docs and validators agree on the widened bounded call subset
- imported, async, opaque, and broader direct-call shapes remain explicitly non-emittable

## Completion evidence

- `scripts/scir_python_bootstrap.py` and `scripts/wasm_backend_metadata.py` now classify `b_direct_call` as Wasm-emittable and admit `H_DIRECT_CALL` only for the bounded helper-free same-module scalar call subset
- `scripts/scir_bootstrap_pipeline.py` now emits stable WAT for the fixed `identity` / `call_identity` shape using plain same-module Wasm `call` with no imports, tables, or helper shims
- `backends/wasm/README.md`, `LOWERING_CONTRACT.md`, and `VALIDATION_STRATEGY.md` now make the widened direct-call subset explicit while keeping imported, indirect, recursive, async, opaque, and broader call-graph shapes out of scope
- `DR-023` records the backend widening, `Q-04-002` is closed, and the execution queue now advances to the next substantive Wasm question rather than back to optional Track `C` governance
