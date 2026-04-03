# SCIR-H Overview
Status: Informative

`SCIR-H` is the canonical semantic layer and the only normative source of truth in the MVP.
`SCIR-Hc` is the derived compressed companion view used for AI-facing lexical comparisons.

## Role

`SCIR-H` makes explicit:

- module boundaries
- imports
- record types
- function signatures
- mutation
- structured control
- field places
- async suspension
- opaque and unsafe boundaries
- semantic lineage

## Active subset

The active canonical subset is the subset implemented by `scripts/scir_h_bootstrap_model.py`.
That subset now includes the importer-only `!throw` effect marker on the bounded Tier `B` `try/catch` slice, while standalone `throw` syntax remains deferred.

Anything broader is deferred until grammar, parser, validator, lowering, reconstruction, and tests agree.

## Dual representation

The active implementation now maintains two `SCIR-H`-family surfaces:

- canonical explicit `SCIR-H` for validation, reconstruction, identity, and preservation claims
- derived compressed `SCIR-Hc` for lexical-efficiency benchmarking and AI-facing transport

`SCIR-Hc` may elide inferable effect rows, return types, and local binding type markers, but it must round-trip back to canonical `SCIR-H` without semantic drift.

## Canonicality rules

- indentation-sensitive suites
- newline-delimited storage
- no comments in canonical storage
- direct calls as `f(args)`
- explicit `var` and `set`
- explicit field places
- deterministic storage for hashing

## Compression rules

- `SCIR-Hc` is generated only from validated `SCIR-H`
- `SCIR-Hc` does not define semantics independently
- `SCIR-Hc` carries a derived-only authority marker plus per-node omission provenance
- lowering, reconstruction, and backend emission must reject direct `SCIR-Hc` input
- boundary capability hoisting stays metadata-only in the current subset
- deferred witness syntax remains deferred in both explicit and compressed views

## Non-goals

`SCIR-H` is not:

- a user-facing authoring language
- a low-level optimizer IR
- the place to hide host or boundary semantics
