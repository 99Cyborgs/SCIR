# SCIR-L Overview
Status: Informative

`SCIR-L` is the derivative control/dataflow layer.

## Role

`SCIR-L` supports:

- CFG reasoning
- SSA value flow
- explicit memory/effect sequencing
- backend preparation
- Wasm reference emission

## Active subset

The active subset is the op set implemented and validated by `scripts/scir_bootstrap_pipeline.py`.

Every meaningful op must have:

- `origin`
- `lowering_rule`

## Non-goals

`SCIR-L` is not:

- a second semantic source of truth
- the default reconstruction source
- a license to invent semantics absent from `SCIR-H`
