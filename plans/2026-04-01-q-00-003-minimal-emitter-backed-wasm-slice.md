# 2026-04-01 Q-00-003 Minimal Emitter-Backed Wasm Slice

Status: complete
Owner: Codex
Date: 2026-04-01

## Objective

Land the first helper-free emitter-backed Wasm slice over the smallest admitted `SCIR-L` subset without widening runtime, parity, or language-support claims.

## Scope

- add stable WAT emission and `l_to_wasm` preservation reporting for the current local-slot clamp shape
- keep emission positive for `fixture.python_importer.a_basic_function` and `fixture.rust_importer.a_mut_local`
- reject `field.addr`, direct call, async, opaque, helper-import, and runtime-shim backend shapes explicitly
- update doctrine, decision/open-question state, and the execution queue to match the landed subset

## Non-goals

- binary `.wasm` emission
- Wasm runtime execution harnesses
- helper-backed imports or linear-memory conventions
- preservation claims stronger than `P2`

## Touched files

- `scripts/scir_bootstrap_pipeline.py`
- `scripts/validate_repo_contracts.py`
- `backends/wasm/README.md`
- `LOWERING_CONTRACT.md`
- `VALIDATION_STRATEGY.md`
- `VALIDATION.md`
- `SPEC_COMPLETENESS_CHECKLIST.md`
- `DECISION_REGISTER.md`
- `OPEN_QUESTIONS.md`
- `EXECUTION_QUEUE.md`
- `reports/examples/preservation_l_to_wasm.example.json`
- `reports/exports/*`

## Invariants that must remain true

- `SCIR-H` remains normative and `SCIR-L` remains derivative
- Wasm claims remain profile `P` with a `P2` ceiling
- unsupported backend shapes remain explicit
- default validation stays Python-first

## Risks

- the current `cmp` op does not encode a predicate, so emission must stay bounded to the existing less-than-zero shape
- queue/export synchronization must stay aligned while resolving `OQ-002`

## Validation steps

- `python scripts/validate_repo_contracts.py --mode validate`
- `python scripts/scir_bootstrap_pipeline.py --mode validate`
- `python scripts/scir_bootstrap_pipeline.py --language rust --mode validate`
- `python scripts/build_execution_queue.py --mode check`
- `python scripts/run_repo_validation.py`
- `python scripts/run_repo_validation.py --require-rust`

## Rollback strategy

Revert the Wasm emitter, doctrine, and queue/export updates as a unit if the bounded subset cannot stay coherent under validation.

## Evidence required for completion

- stable WAT and passing `l_to_wasm` reports exist for the admitted helper-free subset
- unsupported Wasm shapes reject explicitly without helper-backed fallbacks
- doctrine, decision state, open questions, queue state, and derived exports agree with the landed subset
