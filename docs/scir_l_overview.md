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

## Non-goals

`SCIR-L` is not:

- the canonical semantic surface,
- the default reconstruction source,
- a license to invent `SCIR-L`-only semantics.

If a meaning is required for program understanding, it belongs in `SCIR-H` first.

See `specs/scir_l_spec.md`.
