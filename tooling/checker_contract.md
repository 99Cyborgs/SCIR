# Checker Contract
Status: Normative

## Responsibilities

- run repository contract checks,
- run `SCIR-H` and `SCIR-L` validators,
- surface profile, preservation, and tier omissions,
- emit machine-readable report bundles.

## Minimum checks

- required-file presence
- schema parseability
- validator invariant coverage
- report completeness
- benchmark doctrine completeness

## Exit behavior

- hard invariant failures are blocking,
- missing claim annotations are blocking,
- warnings are non-blocking only when the relevant contract allows them.
