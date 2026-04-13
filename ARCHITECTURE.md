# ARCHITECTURE
Status: Normative

## Core doctrine

SCIR is a two-layer system.

| Layer | Status | Purpose |
| --- | --- | --- |
| `SCIR-H` | normative | canonical semantics for inspection, validation, transformation, and reconstruction |
| `SCIR-L` | derivative | lowered control/dataflow form for validation and backend preparation |

`SCIR-H` is the only semantic source of truth.
`SCIR-L` is valid only when it is justified by validated `SCIR-H` plus a named lowering rule.

## Active repository phase

The active phase is:

```text
Frozen 11-case Python proof-loop
  -> Track A / Track B strong-baseline comparison
  -> continuation or stop decision
```

Track `A` and Track `B` are the only active benchmark tracks in this strong-baseline phase.

## Active implementation lane

The implementation lane being audited by that phase is:

```text
Python source
  -> Python subset importer
  -> canonical SCIR-H
  -> SCIR-H validation
  -> focused validator hardening
```

This remains the bounded implementation surface under test. It is not permission to widen semantics during the falsification phase.

## Maintained support lanes

These lanes remain executable but are not current widening targets:

```text
validated SCIR-H
  -> derived SCIR-Hc
  -> derivative SCIR-L
  -> SCIR-L validation
  -> bounded Python reconstruction
  -> bounded Wasm emission
  -> Track A / Track B benchmarks
```

Rust remains importer-first evidence aligned to the same `SCIR-H` contract and is not an auto-activating post-Phase-2 implementation lane.
Wasm remains a retained bounded backend surface aligned to the same derivative `SCIR-L` contract and is not an auto-activating post-proof-loop implementation lane.

## Active `SCIR-H` subset

The executable bootstrap subset currently admits:

- module headers
- `import sym` and `import type`
- record `type` declarations
- `fn` and `async fn`
- `var`
- `set`
- `return`
- `if` / `else`
- `loop`
- `break`
- `continue`
- single-handler `try` / `catch name Type`
- direct call `f(args)`
- `await`
- explicit field places such as `counter.value`
- intrinsic scalar comparisons

Anything broader remains deferred or unsupported until the parser, validator, and tests all agree.
The active proof loop now includes one exact executable `try/catch` slice: a direct call in the `try` body with a fixed `ValueError` fallback that returns `0`.

## Derived and backend posture

- `SCIR-Hc` is a derived compression view over validated `SCIR-H`, never semantic authority.
- `SCIR-L` remains derivative-only and subset-bound.
- Wasm remains a bounded retained reference backend, not a parity claim or the current widening target.
- Benchmarking remains an audit surface over the admitted implementation lane, not permission to rewrite the architecture.

## Architecture change protocol

No architecture change is complete until:

- affected normative specs are current
- validator implications are current
- root docs name the same active boundary
- `DECISION_REGISTER.md` records the architectural decision
- unresolved ambiguity is recorded in `OPEN_QUESTIONS.md`
