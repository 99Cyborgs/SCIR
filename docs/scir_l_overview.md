# SCIR-L Overview
Status: Informative

`SCIR-L` is the lowered control and analysis layer.

## Role

`SCIR-L` exists to support:

- CFG reasoning,
- SSA value flow,
- explicit memory and effect sequencing,
- async lowering,
- witness lowering,
- optimization,
- backend preparation.

## Key properties

- block-parameter SSA style
- explicit region or memory tokens
- explicit effect tokens where ordering matters
- explicit provenance back to `SCIR-H`
- limited reconstructability

## Bootstrap v0.1 freeze

The current executable Phase 3 freeze is intentionally minimal:

- value ops: `const`, `cmp`
- memory ops: `alloc`, `store`, `load`
- place projection: `field.addr`
- effect ops: `call`, `async.resume`, `opaque.call`
- terminators: `ret`, `br`, `cond_br`

`SCIR-L` is still derivative. Phase 6A widens it only enough to support Rust borrowed-record field places through `field.addr`; it does not authorize witness ops, enum lowering, or optimizer growth ahead of source coverage.

Phase 6B keeps the frozen op set unchanged. It adds only a profile-gated optimization contract plus benchmark-only post-`SCIR-L` emitters for the fixed Rust `N` and Python `D-PY` Track `D` slices. Those emitters are measurement scaffolding, not reconstruction evidence or a new backend surface.

## Non-goals

`SCIR-L` is not:

- the canonical semantic surface,
- the default reconstruction source,
- a license to invent `SCIR-L`-only semantics.

If a meaning is required for program understanding, it belongs in `SCIR-H` first.

See `specs/scir_l_spec.md`.
