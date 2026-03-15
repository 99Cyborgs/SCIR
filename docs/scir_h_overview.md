# SCIR-H Overview
Status: Informative

`SCIR-H` is the canonical semantic layer.

## Role

`SCIR-H` exists to make these explicit:

- module and symbol boundaries,
- types,
- effects,
- capabilities,
- witness passing,
- ownership and alias modes,
- control structure,
- mutation sites,
- unsafe and opaque boundaries,
- stable IDs and provenance.

## Design constraints

`SCIR-H` must be:

- canonical enough for formatting and diff stability,
- structured enough for reconstruction,
- explicit enough for validation,
- regular enough for AI-facing editing,
- small enough to avoid semantic sprawl.

## Canonicality rules

- one declaration form per construct kind,
- sorted imports,
- topologically ordered declarations,
- stable identifiers on public structure,
- no hidden conversions,
- no hidden ambient capabilities,
- no comments in canonical storage.

## Non-goals

`SCIR-H` is not:

- a user-friendly mainstream language,
- a low-level optimizer IR,
- a raw source AST,
- a place to preserve every source-language accident.

See `specs/scir_h_spec.md`.
