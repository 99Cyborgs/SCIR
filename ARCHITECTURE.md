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

## Active implementation lane

The active lane is:

```text
Python source
  -> Python subset importer
  -> canonical SCIR-H
  -> SCIR-H validation
  -> focused validator hardening
```

This is the current widening target.

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

Rust remains importer-first evidence aligned to the same `SCIR-H` contract.

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

## Derived and backend posture

- `SCIR-Hc` is a derived compression view over validated `SCIR-H`, never semantic authority.
- `SCIR-L` remains derivative-only and subset-bound.
- Wasm remains a bounded reference backend, not a parity claim.
- Benchmarking remains a retained audit surface, not the current implementation driver.

## Architecture change protocol

No architecture change is complete until:

- affected normative specs are current
- validator implications are current
- root docs name the same active boundary
- `DECISION_REGISTER.md` records the architectural decision
- unresolved ambiguity is recorded in `OPEN_QUESTIONS.md`
